from os.path import isfile
from pathlib import Path

import pytest

from unitranscode.transcoder import Transcoder


def test_edit(example_20s_wav_file: Path, temp_folder: Path):
    in_file = example_20s_wav_file
    transcoder = Transcoder()

    cuts = [(0.0, 1.0), (3.0, 4.5), (7.0, 10.0)]

    out_file = transcoder.edit(
        in_file, cuts, temp_folder.joinpath('output.wav')
    )

    assert isfile(out_file)

    out_file_duration = transcoder.info(out_file).duration_s
    expected_duration = sum([end - start for start, end in cuts])
    assert out_file_duration == pytest.approx(expected_duration, 0.1)


def test_extract_cuts(example_20s_wav_file: Path, temp_folder: Path):
    in_file = example_20s_wav_file
    transcoder = Transcoder()

    cuts = [(0.0, 1.0), (3.0, 4.5), (7.0, 10.0)]
    out_files = transcoder.extract_cuts(
        in_file, cuts, str(temp_folder.joinpath('out-%d.wav'))
    )

    assert transcoder.info(out_files[0]).duration_s == pytest.approx(1.0)
    assert transcoder.info(out_files[1]).duration_s == pytest.approx(1.5)
    assert transcoder.info(out_files[2]).duration_s == pytest.approx(3.0)


def test_transcode_wav(example_20s_wav_file: Path, temp_folder: Path):
    transcoder = Transcoder()
    out_file = transcoder.transcode(
        str(example_20s_wav_file),
        str(temp_folder.joinpath('output.wav')),
        audio_codec='pcm_s16le',
    )
    assert (
        transcoder.info(example_20s_wav_file).duration_s
        == transcoder.info(out_file).duration_s
    )
