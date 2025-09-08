# MKV Scripts

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Made with](https://img.shields.io/badge/made%20with-MKVToolNix-orange.svg)](https://mkvtoolnix.download/)

Cross-platform Python utilities for automated video file processing using MKVToolNix tools.

## 🎯 Features

- **Audio Track Processing**: Remove non-English audio tracks while preserving English content
- **Cross-Platform Support**: Windows, Linux, and macOS compatibility
- **Safety First**: Atomic operations with temporary files and comprehensive logging
- **Dry Run Mode**: Test operations without modifying files
- **Batch Processing**: Recursive directory processing with progress tracking
- **UTF-8 Support**: International filename and metadata handling

## 📁 Repository Structure

```
mkvScripts/
├── scripts/
│   ├── audio/              # Audio track processing utilities
│   │   └── remove_non_english_audio.py
│   ├── subtitle/           # Subtitle processing utilities (planned)
│   └── container/          # Container manipulation utilities (planned)
├── examples/               # Usage examples and test cases
└── .gitignore             # Git ignore patterns
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.6+**
- **MKVToolNix** - Download from [mkvtoolnix.download](https://mkvtoolnix.download/)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mkvScripts
```

2. Ensure MKVToolNix is installed and accessible in your PATH

### Usage

#### Remove Non-English Audio Tracks

**Dry run (recommended first):**
```bash
# Windows
python scripts/audio/remove_non_english_audio.py "C:\Videos" --dry-run

# Linux/macOS
python scripts/audio/remove_non_english_audio.py "/home/user/videos" --dry-run
```

**Process files:**
```bash
# Windows
python scripts/audio/remove_non_english_audio.py "C:\Videos"

# Linux/macOS
python scripts/audio/remove_non_english_audio.py "/home/user/videos"
```

**Custom MKVToolNix path:**
```bash
python scripts/audio/remove_non_english_audio.py "/path/to/videos" --mkv-tools-path "/usr/local/bin"
```

## 📋 Supported Formats

- `.mkv` `.mp4` `.avi` `.m4v` `.mov` `.wmv` `.flv` `.webm`

## 🛡️ Safety Features

- **Atomic Operations**: Uses temporary files to prevent corruption
- **Backup Recommendation**: Always backup your files before processing
- **Comprehensive Logging**: All operations logged to `mkv_audio_removal.log`
- **Error Recovery**: Graceful handling of corrupted or unsupported files
- **Dry Run Mode**: Test operations without making changes

## 🌍 Language Support

The script automatically detects and preserves English audio tracks using these language codes:
- `en`, `eng`, `english`, `en-US`, `en-GB`

## 🔧 Platform-Specific Notes

### Windows
- Supports UNC paths
- Searches common installation paths: `C:\Program Files\MKVToolNix`

### Linux
- Searches standard paths: `/usr/bin`, `/usr/local/bin`, `/opt/mkvtoolnix/bin`
- Supports Homebrew installations

### macOS
- Standard Unix paths with Homebrew support

## ⚠️ Important Notes

- **Always backup your video files before running any processing scripts**
- Test with `--dry-run` flag first to preview changes
- The script modifies files in-place using atomic operations
- Processing large files may take time depending on file size and system performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style and safety patterns
4. Test thoroughly with `--dry-run` mode
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MKVToolNix](https://mkvtoolnix.download/) - The powerful multimedia toolkit that makes this project possible