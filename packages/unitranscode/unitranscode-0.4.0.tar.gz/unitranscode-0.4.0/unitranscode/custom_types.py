from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class AudiogramOp:
    image_path: str
    waveform_sx: int
    waveform_sy: int
    waveform_offsetx: int
    waveform_offsety: int
    waveform_color_hex: str


class UnitranscodeFormatError(RuntimeError):
    pass


class UnitranscodeExecError(UnitranscodeFormatError):
    def __init__(self, msg_cmd, /):
        if isinstance(msg_cmd, str):
            self.message = msg_cmd
            self.command = []
        else:
            self.message, self.command = msg_cmd
        super().__init__(self.message)

    def __repr__(self):
        return 'UnitranscodeExecError(message={}, command={})'.format(
            self.message, self.command
        )


class EncodingInfo(dict):
    @property
    def sample_rate_maybe(self):
        return (
            self.audio_streams[0].get('sample_rate')
            if self.audio_streams
            else None
        )

    @property
    def video_streams(self):
        video_streams = [
            i for i in self['streams'] if i['codec_type'] == 'video'
        ]
        # Remove strange 'video' format types like MJPEG
        if len(video_streams) > 1:
            video_streams = [
                i for i in video_streams if i.get('avg_frame_rate') != '0/0'
            ] or video_streams
        return video_streams

    @property
    def audio_streams(self):
        return [i for i in self['streams'] if i['codec_type'] == 'audio']

    @property
    def video_stream_maybe(self):
        if len(self.video_streams) != 1:
            return None
        return self.video_streams[0]

    @property
    def video_stream(self):
        if not self.video_stream_maybe:
            raise UnitranscodeFormatError(
                f'Invalid number of video streams: {len(self.video_streams)}'
            )
        return self.video_stream_maybe

    @property
    def audio_stream_maybe(self):
        if len(self.audio_streams) != 1:
            return None
        return self.audio_streams[0]

    @property
    def audio_stream(self):
        if not self.audio_stream_maybe:
            raise UnitranscodeFormatError(
                f'Invalid number of audio streams: {len(self.audio_streams)}'
            )
        return self.audio_stream_maybe

    @property
    def duration_s(self) -> float:
        try:
            return float(self['format']['duration'])
        except (ValueError, KeyError):
            raise UnitranscodeFormatError('No duration recorded in format')

    @property
    def avg_fps(self) -> Optional[float]:
        num, den = self.video_stream['avg_frame_rate'].split('/')
        num, den = int(num), int(den)
        if den == 0:
            return None
        return num / den


class ProgressInfo(dict):
    def __init__(self, data: dict, duration_s: float = None):
        super().__init__(data, duration_s=duration_s or data.get('duration_s'))

    @property
    def duration_s(self):
        if self['duration_s'] is None:
            raise RuntimeError('Duration not passed to ProgressInfo!')
        return self['duration_s']

    @property
    def progress_seconds(self) -> float:
        if 'time' not in self:
            return float('NaN')
        hh, mm, ss = self['time'].split(':')
        return int(hh) * 60 * 60 + int(mm) * 60 + float(ss)

    def progress(self, duration_s: float) -> float:
        return self.progress_seconds / duration_s

    @property
    def ratio_complete(self):
        return self.progress_seconds / self.duration_s


ProgressHandler = Callable[[ProgressInfo], None]

video_extensions = ['.mp4', '.mov', '.webm', '.mkv', '.avi', '.wmv']
