import atexit
import json
import os
import re
import shutil
import threading

from concurrent.futures import CancelledError, Future, ThreadPoolExecutor
from contextlib import nullcontext, suppress
from functools import cached_property, lru_cache
from os.path import abspath, isfile, splitext
from signal import SIGCONT, SIGTSTP
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile
from threading import Lock
from time import sleep
from typing import List, Optional, Tuple, Union

from loguru import logger

from .custom_types import (
    AudiogramOp,
    EncodingInfo,
    ProgressHandler,
    ProgressInfo,
    UnitranscodeExecError,
    UnitranscodeFormatError,
    video_extensions,
)
from .utils import remove_prefix_suffix


class FfmpegOperation:
    def __init__(
        self,
        transcoder: 'Transcoder',
    ):
        self.transcoder = transcoder
        self.input_files: Optional[List[str]] = None
        self.output_files: Optional[List[str]] = None
        self.cmd: Optional[list] = None
        self._proc: Optional[Popen] = None
        self.is_paused = False
        self.cancelled = False
        self.pause_lock = Lock()
        self.stdout_chunks = []
        self.stderr_chunks = []
        self.future: Optional[Future] = None

    @property
    def pid(self):
        return self._proc.pid

    @property
    def proc(self) -> Optional[Popen]:
        return self._proc

    @proc.setter
    def proc(self, value):
        with self.pause_lock:
            self._proc = value
            if self._proc:
                if self.is_paused:
                    self.pause(_with_lock=False)
                else:
                    self.resume(_with_lock=False)

    @staticmethod
    def resume_pid(pid: int):
        os.kill(pid, SIGCONT)

    @staticmethod
    def pause_pid(pid: int):
        os.kill(pid, SIGTSTP)

    def pause(self, _with_lock=True):
        with self.pause_lock if _with_lock else nullcontext():
            self.is_paused = True
            if self._proc:
                try:
                    self.pause_pid(self.proc.pid)
                except ProcessLookupError:
                    assert (
                        self._proc.poll() is not None
                    ), 'Error: Process not terminated, but failed to find PID'

    def resume(self, _with_lock=True):
        with self.pause_lock if _with_lock else nullcontext():
            self.is_paused = False
            if self._proc:
                try:
                    self.resume_pid(self.proc.pid)
                except ProcessLookupError:
                    assert (
                        self._proc.poll() is not None
                    ), 'Error: Process not terminated, but failed to find PID'

    def cancel(self):
        with self.pause_lock:
            self.cancelled = True
            if self._proc:
                self._proc.kill()

    @cached_property
    def input_files_info(self) -> List[EncodingInfo]:
        return [self.transcoder.info(i) for i in self.input_files]

    @property
    def stdout_bytes(self):
        return b''.join(self.stdout_chunks)

    @property
    def stderr_bytes(self):
        return b''.join(self.stderr_chunks)

    def exec_error(self, return_code: int, info=''):
        assert self.cmd
        full_cmd = ' '.join("'{}'".format(i) for i in self.cmd)
        debug_cmd_output = self.stdout_bytes.decode(
            errors='ignore'
        ) + self.stderr_bytes.decode(errors='ignore')
        return UnitranscodeExecError(
            (
                f'Failed to run ffmpeg ({return_code}): {info}'
                f'{debug_cmd_output}\n'
                f'Full command: {full_cmd}',
                self.cmd,
            )
        )


class Transcoder:
    _ffmpeg_data_matcher = re.compile(r'([a-zA-Z]\S*)\s*=\s*(\S+)')
    _ffmpeg_progress_end = [b'\r', b'\n']
    _ffmpeg_progress_args = ['-stats']

    def __init__(self, ffmpeg_path=None, ffprobe_path=None):
        self._ffmpeg = ffmpeg_path or shutil.which('ffmpeg')
        self._ffprobe = ffprobe_path or shutil.which('ffprobe')
        self.default_ffmpeg_args = '-y -hide_banner -v warning '.split()
        self.default_fps = 60
        self.max_fps = 60
        self.debug = False
        self._shutting_down = False
        self.in_progress_ops = set()

        for var, binary in [
            (self._ffmpeg, 'ffmpeg'),
            (self._ffprobe, 'ffprobe'),
        ]:
            if not var:
                raise RuntimeError(f'Failed to find {binary} in path!')

    def op(self):
        return FfmpegOperation(self)

    def ffmpeg(
        self,
        *args,
        duration_s=None,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ) -> FfmpegOperation:
        op = op or self.op()
        op.cmd = [
            self._ffmpeg,
            *self.default_ffmpeg_args,
            *(self._ffmpeg_progress_args * bool(on_progress)),
            *args,
        ]
        proc = op.proc = Popen(op.cmd, stdout=PIPE, stderr=PIPE)
        if on_progress:
            self._track_progress(on_progress, proc, op, duration_s)
        stdout, stderr = proc.communicate()
        op.stdout_chunks.append(stdout)
        op.stderr_chunks.append(stderr)

        if proc.returncode == -9 and (self._shutting_down or op.cancelled):
            raise CancelledError('Ffmpeg operation cancelled')
        if proc.returncode != 0:
            raise op.exec_error(proc.returncode)
        return op

    def chop(
        self,
        in_file: str,
        out_file: str,
        pos_start_s: float = None,
        pos_end_s: float = None,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
        force_no_transcode: bool = True,
    ) -> str:
        op = op or self.op()
        assert force_no_transcode, 'Transcoding not supported yet for chop'
        assert (
            pos_start_s is None or pos_end_s is not None
        ), 'Must specify either start or end position to chop to'
        self.ffmpeg(
            *['-i', in_file],
            *['-c', 'copy'],
            *['-ss', str(pos_start_s)] * (pos_start_s is not None),
            *['-to', str(pos_end_s)] * (pos_end_s is not None),
            out_file,
            duration_s=self.info(in_file).duration_s if on_progress else None,
            on_progress=on_progress,
            op=op,
        )
        return out_file

    def _track_progress(
        self,
        on_progress: ProgressHandler,
        proc: Popen,
        op: FfmpegOperation,
        duration_s: float,
    ):
        buffer = bytearray()
        while True:
            chunk = proc.stderr.read(1)
            if not chunk:
                break
            buffer.append(chunk[0])
            if any(buffer.endswith(i) for i in self._ffmpeg_progress_end):
                chunk = buffer
                progress_data = {
                    m.group(1): m.group(2)
                    for m in self._ffmpeg_data_matcher.finditer(chunk.decode())
                }
                if progress_data:
                    on_progress(ProgressInfo(progress_data, duration_s))
                else:
                    op.stdout_chunks.append(chunk)
                buffer = bytearray()

    def loudnorm_info(
        self,
        in_file: str,
        level=-20.0,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ) -> dict:
        assert isinstance(
            level, (float, int)
        ), f'level {level!r} is not a number'
        op = self.ffmpeg(
            *['-v', 'info'],
            *['-i', in_file],
            *[
                '-filter_complex',
                (
                    f'[0:0]loudnorm=i={level}:lra=7.0:'
                    f'tp=-2.0:offset=0.0:print_format=json'
                ),
            ],
            *['-vn', '-sn', '-f', 'null', '/dev/null'],
            duration_s=self.info(in_file).duration_s if on_progress else None,
            op=op,
            on_progress=on_progress,
        )
        bracket_blobs: List[bytes] = re.findall(rb'{[^{}]*}', op.stderr_bytes)
        if not bracket_blobs:
            bracket_blobs = re.findall(rb'{[^{}]*}', op.stdout_bytes)
            if not bracket_blobs:
                raise op.exec_error(0, 'Unexpected ouput')
        return json.loads(bracket_blobs[-1].decode(errors='ignore'))

    def normalize(
        self,
        in_file: str,
        out_file: str,
        norm_info: dict,
        level=-20.0,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ):
        norm_info = {
            k: '0.0' if v in ['inf', '-inf'] else v
            for k, v in norm_info.items()
        }
        in_file_info = self.info(in_file)
        if not in_file_info.sample_rate_maybe and in_file_info.audio_streams:
            logger.error(
                'Unknown sample rate for audio file: {}', in_file_info
            )
        self.ffmpeg(
            *['-i', in_file],
            *[
                '-filter_complex',
                (
                    f'[0:0]'
                    f'loudnorm=i={level}:lra=7.0:tp=-2.0:offset=0.29:'
                    f'measured_i={norm_info["input_i"]}:'
                    f'measured_lra={norm_info["input_lra"]}:'
                    f'measured_tp={norm_info["input_tp"]}:'
                    f'measured_thresh={norm_info["input_thresh"]}:'
                    f'linear=true:print_format=json'
                    f'[norm0]'
                ),
            ],
            *['-map_metadata', '0'],
            *['-map_metadata:s:a:0', '0:s:a:0'],
            *['-map_chapters', '0'],
            *['-c:v', 'copy'],
            *['-map', '[norm0]'],
            *['-c:a:0', 'pcm_s16le'],
            *['-c:s', 'copy'],
            *(
                ['-ar', f'{in_file_info.sample_rate_maybe}']
                * bool(in_file_info.sample_rate_maybe)
            ),
            out_file,
            duration_s=in_file_info.duration_s if on_progress else None,
            on_progress=on_progress,
            op=op,
        )
        return out_file

    def info(
        self, filename: str, count_frames=False, can_retry=True
    ) -> EncodingInfo:
        if not isfile(filename):
            raise OSError('No such file: {}'.format(filename))
        file_size = None  # noqa
        with suppress(OSError):
            file_size = os.path.getsize(filename)
        p = Popen(
            [self._ffprobe] + '-v quiet -print_format json '
            '-show_format -show_streams'.split()
            + ['-count_frames'] * count_frames
            + [filename],
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = p.communicate()
        info_json = json.loads(stdout) if p.returncode == 0 else None
        if not info_json:
            output = (stdout * (p.returncode != 1) + stderr).strip()
            logger.warning(
                'Failed to interpret file: (filesize={}, name={}, output="{}")',
                file_size,
                filename,
                output,
            )
            if (file_size is None or file_size < 1000) and can_retry:
                logger.warning('Retrying ffprobe...')
                sleep(0.5)
                return self.info(filename, count_frames, False)
            raise UnitranscodeFormatError(
                output or 'Error parsing media file!'
            )
        return EncodingInfo(info_json)

    @staticmethod
    def _handle_amix(
        args: list, infos: List[EncodingInfo], audio_indices: List[int]
    ):
        audio_count = sum(len(infos[i].audio_streams) for i in audio_indices)
        if audio_count > 1:
            amerge_inputs = ''.join(f'[{i}]' for i in audio_indices)
            args.extend(
                [
                    '-filter_complex',
                    f'{amerge_inputs}amix=inputs={audio_count}',
                ]
            )
            return True
        return False

    def _shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        for op in list(self.in_progress_ops):
            proc = op.proc
            if proc:
                with suppress(OSError):
                    proc.kill()

    def transcode(
        self,
        input: Union[str, List[str]],
        output: str,
        channels: Optional[int] = None,
        sample_rate: Optional[int] = None,
        audio_index: int = None,
        video_index: int = None,
        audio_codec: str = None,
        mix_down=True,
        extra_args: list = None,
        on_progress: ProgressHandler = None,
        audiogram_op: Union[AudiogramOp, dict] = None,
        op: FfmpegOperation = None,
    ) -> str:
        op = op or self.op()
        op.input_files = [input] if isinstance(input, str) else list(input)
        infos = op.input_files_info
        args = []
        for i in op.input_files:
            args.extend(['-i', i])
        if audiogram_op:
            if isinstance(audiogram_op, dict):
                audiogram_op = AudiogramOp(**audiogram_op)
            args.extend(['-i', audiogram_op.image_path])
        if channels is not None:
            args.extend(['-ac', str(channels)])
        if sample_rate is not None:
            args.extend(['-ar', str(sample_rate)])
        audio_indices = (
            [*range(len(infos))] if audio_index is None else [audio_index]
        )
        did_mix = (
            False
            if not mix_down
            else self._handle_amix(args, infos, audio_indices)
        )
        if not did_mix and audio_index is not None:
            args.extend(['-map', f'{audio_index}:a'])
        video_indices = (
            [*range(len(infos))] if video_index is None else [video_index]
        )
        try:
            duration_s = max(i.duration_s for i in infos)
        except UnitranscodeFormatError:
            duration_s = None
        video_streams = [
            (i, infos[i].video_stream)
            for i in video_indices
            if len(infos[i].video_streams) > 0
        ]
        maybe_args = []
        output_ext = splitext(output)[-1].lower()
        output_has_video = output_ext in video_extensions
        if output_ext in ['.mp3', '.aac']:
            args.extend(['-b:a', '192k'])
        input_has_video = len(video_streams) > 0
        convert_video = (
            input_has_video and output_has_video and not audiogram_op
        )
        if convert_video:
            if len(video_streams) > 1:
                raise UnitranscodeFormatError(
                    'Multiple video streams detected'
                )
            video_index, video_stream = video_streams[0]
            args.extend(['-map', f'{video_index}:v'])
            args.extend(['-vsync', '2'])
            if splitext(output)[-1].lower() == '.mp4':
                args.extend(['-level', '3.1'])
            extra_maybe_args = []
            if (
                video_stream['width'] % 2 != 0
                or video_stream['height'] % 2 != 0
            ):
                extra_maybe_args.append(
                    (['-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2'], [])
                )
            incompatible = (
                video_stream['codec_name'] == 'vp8' and output_ext == '.mp4'
            )
            if not incompatible:
                extra_maybe_args = [(['-c:v', 'copy'], extra_maybe_args)]
            maybe_args.extend(extra_maybe_args)
        if not output_has_video and audiogram_op:
            raise UnitranscodeFormatError(
                f'Cannot generate audiogram to audio file extension {output_ext}'
            )
        if audiogram_op:
            waveform_size = (
                f'{audiogram_op.waveform_sx}x{audiogram_op.waveform_sy}'
            )
            color_hex = audiogram_op.waveform_color_hex
            overlay_offset = (
                f'{audiogram_op.waveform_offsetx}:'
                f'{audiogram_op.waveform_offsety}'
            )
            args.extend(
                [
                    '-filter_complex',
                    f'[0:a]showwaves=s={waveform_size}:'
                    f'colors=0x{color_hex}:mode=cline,format=rgba[v];'
                    f'[1:v][v]overlay={overlay_offset}[outv]',
                    '-map',
                    '[outv]:v',
                    '-map',
                    '0:a',
                ]
            )

        audio_infos = [
            infos[i].audio_stream
            for i in audio_indices
            if infos[i].audio_stream_maybe
        ]
        if not audio_infos:
            raise UnitranscodeFormatError(
                'Input does not have any audio channels!'
            )

        if audio_codec:
            if not did_mix and audio_infos[0].get('codec_name') == audio_codec:
                args.extend(['-c:a', 'copy'])
            else:
                args.extend(['-c:a', audio_codec])

        if not did_mix and not audio_codec:
            audio_info = audio_infos[0]
            incompatible = False
            if (
                sample_rate is not None
                and audio_info['sample_rate'] != sample_rate
            ):
                incompatible = True
            if channels is not None and audio_info['channels'] != channels:
                incompatible = True
            codec_name = audio_info.get('codec_name', '')
            input_audio_is_wav = codec_name.startswith('pcm_')
            output_is_wav = output_ext in ['.wav', '.wave']
            # ffmpeg will incorrectly encode audio to non-container formats
            if not output_has_video:
                if not (input_audio_is_wav and output_is_wav):
                    incompatible = True
            if input_audio_is_wav and (output_ext in ['.mp4', '.webm']):
                incompatible = True
            if not incompatible:
                maybe_args.append((['-c:a', 'copy'], []))
        while True:
            try:
                all_maybe_args = sum([args for args, extra in maybe_args], [])
                self.ffmpeg(
                    *args,
                    *all_maybe_args,
                    output,
                    op=op,
                    on_progress=on_progress,
                    duration_s=duration_s,
                    *(extra_args or []),
                )
            except UnitranscodeFormatError:
                if not maybe_args:
                    raise
                _, new_maybe_args = maybe_args.pop()
                maybe_args.extend(new_maybe_args)
            else:
                break
        return output

    def combine(
        self,
        in_files: List[str],
        out_file: str,
        calc_duration=False,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ):
        op = op or self.op()
        op.input_files = in_files
        op.output_files = [out_file]
        if len(in_files) == 1:
            shutil.copy(in_files[0], out_file)
            return out_file
        with NamedTemporaryFile(
            mode='w', suffix='.txt', delete=not self.debug
        ) as tmp:
            for in_file in in_files:
                tmp.write(f"file '{abspath(in_file)}'\n")
            tmp.flush()
            duration_s = None
            if calc_duration:
                duration_s = sum(i.duration_s for i in op.input_files_info)
            self.ffmpeg(
                '-f',
                'concat',
                '-safe',
                '0',
                '-i',
                tmp.name,
                '-c',
                'copy',
                out_file,
                duration_s=duration_s,
                on_progress=on_progress,
                op=op,
            )
        return out_file

    def edit(
        self,
        in_file: str,
        cuts: List[Tuple[float, float]],
        output_file: str,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ) -> str:
        op = op or self.op()
        info = self.info(in_file)
        has_video = bool(info.video_stream_maybe)
        has_audio = bool(info.audio_stream_maybe)
        filter_cmds = []
        stream_names = []
        for i, (lt, rt) in enumerate(cuts):
            cmd = ''
            name = ''
            if has_video:
                cmd += f'[0:v]trim={lt}:{rt},setpts=PTS-STARTPTS[v{i}];'
                name += f'[v{i}]'
            if has_audio:
                cmd += f'[0:a]atrim={lt}:{rt},asetpts=PTS-STARTPTS[a{i}];'
                name += f'[a{i}]'
            filter_cmds.append(cmd)
            stream_names.append(name)
        video_output = '[v]' * has_video
        audio_output = '[a]' * has_audio
        complex_filter = (
            ''.join(filter_cmds)
            + ''.join(stream_names)
            + f'concat=n={str(len(stream_names))}'
            + f':v={[0, 1][has_video]}:a={[0, 1][has_audio]}'
            + video_output
            + audio_output
        )

        self.ffmpeg(
            *('-i', in_file),
            *('-filter_complex', complex_filter),
            *('-map', video_output) * has_video,
            *('-map', audio_output) * has_audio,
            '-shortest',
            output_file,
            duration_s=sum(b - a for a, b in cuts),
            on_progress=on_progress,
            op=op,
        )
        return output_file

    @staticmethod
    def _format_duration(dur: float) -> str:
        mins, secs = divmod(dur, 60.0)
        hours, mins = divmod(dur, 60.0)
        return f'{int(hours):02}:{int(mins):02}:{secs:.03}'

    @staticmethod
    def _chunks(arr, n):
        for i in range(0, len(arr), n):
            yield arr[i : i + n]

    def extract_cuts(
        self,
        in_file: str,
        cuts: List[Tuple[float, float]],
        out_file_fmt='{in_base}-%d.{in_ext}',
        on_progress: ProgressHandler = None,
        batch_size=8,
        op: FfmpegOperation = None,
    ):
        total = 0
        out_files = []
        for cuts_batch in self._chunks(cuts, batch_size):
            out_files.extend(
                self._extract_cuts_direct(
                    in_file=in_file,
                    cuts=cuts_batch,
                    out_file_fmt=out_file_fmt,
                    n_offset=total,
                    on_progress=on_progress,
                    op=op,
                )
            )
            total += len(cuts_batch)
        return out_files

    def _extract_cuts_direct(
        self,
        in_file: str,
        cuts: List[Tuple[float, float]],
        out_file_fmt='{in_base}-%d.{in_ext}',
        n_offset=0,
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ):
        op = op or self.op()
        op.input_files = [in_file]
        in_base, in_ext = splitext(in_file)
        in_ext = in_ext.lstrip('.')
        out_file_fmt = out_file_fmt.format(in_base=in_base, in_ext=in_ext)
        args = [
            *('-i', in_file),
        ]
        out_files = []
        for clip_num, (clip_start, clip_end) in enumerate(cuts, n_offset):
            out_file = out_file_fmt.replace('%d', str(clip_num))
            args += [
                *('-ss', str(clip_start)),
                *('-to', str(clip_end)),
                *('-reset_timestamps', '1'),
                out_file,
            ]
            out_files += [out_file]
        op.output_files = out_files
        self.ffmpeg(
            *args,
            duration_s=self.info(in_file).duration_s,
            on_progress=on_progress,
            op=op,
        )
        return out_files

    def split(
        self,
        in_file: str,
        split_timestamps: Optional[List[float]],
        out_file_fmt='{in_base}-%d.{in_ext}',
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ):
        op = op or self.op()
        op.input_files = [in_file]
        in_base, in_ext = splitext(in_file)
        in_ext = in_ext.lstrip('.')
        out_file_fmt = out_file_fmt.format(in_base=in_base, in_ext=in_ext)
        # noinspection PySimplifyBooleanCheck
        if split_timestamps == []:
            out_file = out_file_fmt.replace('%d', '0')
            shutil.copy(in_file, out_file)
            op.output_files = [out_file]
            return op.output_files
        args = [
            *('-i', in_file),
            *('-c', 'copy'),
            *('-reset_timestamps', '1'),
            *('-f', 'segment'),
            *('-v', 'info'),  # To retain "Opening '{}' for writing" messages
        ]
        if split_timestamps is not None:
            args.extend(
                ['-segment_times', ','.join(str(i) for i in split_timestamps)]
            )
        args.append(out_file_fmt)
        self.ffmpeg(
            *args,
            duration_s=self.info(in_file).duration_s,
            on_progress=on_progress,
            op=op,
        )
        pre, suff = out_file_fmt.encode().split(b'%d')
        out_filenames_raw = sorted(
            re.findall(
                rb"^\s*\[[^]]*]\s*Opening '(.*)' for writing\s*$",
                (
                    op.stderr_bytes.replace(b'\r', b'\n')
                    + b'\n'
                    + op.stdout_bytes.replace(b'\r', b'\n')
                ),
                re.MULTILINE,
            ),
            key=lambda x: int(remove_prefix_suffix(x, pre, suff)),
        )
        # We assume filenames don't have any non-utf8 characters
        op.output_files = [i.decode() for i in out_filenames_raw]
        return op.output_files

    def chunk(
        self,
        in_file: str,
        split_size_seconds: Optional[int] = None,
        out_file_format='{in_base}-%d.{in_ext}',
        on_progress: ProgressHandler = None,
        op: FfmpegOperation = None,
    ):
        op = op or self.op()
        op.input_files = [in_file]
        info = op.input_files_info[0]
        splits = None
        if split_size_seconds is not None:
            num_splits = int(info.duration_s / split_size_seconds)
            splits = [i * split_size_seconds for i in range(1, num_splits + 1)]
        return self.split(
            in_file, splits, out_file_format, on_progress=on_progress, op=op
        )

    @lru_cache(1)
    def _thread_pool(self) -> ThreadPoolExecutor:
        getattr(threading, '_register_atexit', atexit.register)(self._shutdown)
        return ThreadPoolExecutor(
            max_workers=32, thread_name_prefix='transcoder'
        )

    def defer(self, method, **kwargs) -> FfmpegOperation:
        assert any(method.__func__ is i for i in vars(Transcoder).values())
        op = kwargs.pop('op', None) or self.op()
        kwargs['op'] = op
        self.in_progress_ops.add(op)
        op.future = self._thread_pool().submit(method, **kwargs)
        op.future.add_done_callback(lambda _: self.in_progress_ops.remove(op))
        return op
