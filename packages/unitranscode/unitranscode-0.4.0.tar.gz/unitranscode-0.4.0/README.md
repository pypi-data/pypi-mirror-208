# Unitranscode

*Universal transcoding library*

Unitranscode is a Python library for efficient manipulation of various media formats in an automated way. Currently it abstracts a number of FFMPEG processes into a nice API while also handling various edge cases and providing good defaults.

**Features:**

 - [x] Convert between filetypes
   - [x] Automatically skip transcoding if possible
   - [x] Track realtime progress of operation based on ffmpeg output
   - [x] Easily pause and resume processing (via signals to ffmpeg process)
   - [x] Edge case handling (ie. multiple audio tracks, odd pixel resolutions, etc.)
 - [x] Split into chunks or at timestamps without transcoding
 - [x] Combine chunks into single media file without transcoding
 - [x] Media information as json
 - [x] Audio normalization
 - [x] Audiogram generation (creating waveform video from audio-only input)

## Installation

Install via PyPI:

```
pip3 install unitranscode
```

In addition to installing the Python package you will also have to make sure you have the `ffmpeg` and `ffprobe` executables installed to your system (`sudo apt-get install -y ffmpeg`).

## Development

All contributions are welcome. Feel free to create an issue if you have anty specific proposals or issues.

Contribution areas:

 - [ ] Simple CLI
 - [ ] More functionality from FFMPEG
 - [ ] Better support for more formats and edge cases
