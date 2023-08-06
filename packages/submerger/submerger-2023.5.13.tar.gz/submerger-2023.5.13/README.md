# Submerger

Watching movies in a foreign language with dual subtitles is a good way to learn that language. However, most of the subtitles are in a single language. This project aims to overcome that barrier by providing the functionality to create dual subtitles by merging two separate subtitle files.

<div align="center">
  <img src="images/dualsub_example.png" alt="Dualsubtitle example">
</div>

## System requirements

Python >= 3.10

## Install
```bash
pip install submerger
```

### Install for development
You have to include `$HOME/.local/bin` to your `$PATH`. Simply add `export PATH="$HOME/.local/bin:$PATH"` to `.bashrc`.

```bash
pip install --prefix=$(python -m site --user-base) --editable .
```

NOTE: `--prefix=$(python3 -m site --user-base)` is a workaround for a known [`setuptools` issue](https://github.com/pypa/setuptools/issues/3063)

## Usage

### Merge two .srt files
```bash
submerge --subtitles subtitle1.srt subtitle2.srt --output dualsub.srt
```

### Create a dual subtitles by extracting embedded subtitles from a video file
```bash
submerge --video video.mkv --language eng ger --output dualsub.srt
```

### Merge subtitles for all videos in a directory
```bash
submerge --global --language eng ger --directory path/to/series
```

### Check for available subtitles
```bash
ffprobe -loglevel error -print_format json video.mkv -print_format json -show_entries "stream=index:stream_tags=language" -select_streams s
```

## Testing

### Run unit tests
```bash
python scripts/run_tests.py --unit
```

### Run integration tests
```bash
python scripts/run_tests.py --integration
```

### Run lint tests
```bash
python scripts/run_tests.py --lint
```

### Or run periodically with `watch`
```bash
watch python scripts/run_tests.py --all
```

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
