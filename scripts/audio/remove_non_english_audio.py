#!/usr/bin/env python3
"""
MKV Non-English Audio Track Remover

WARNING: This script modifies video files directly. BACKUP YOUR FILES BEFORE RUNNING!

This script recursively processes video files in a directory and removes all
non-English audio tracks using MKVToolNix tools. It also sets the first English
audio track as the default track.

Part of the mkvScripts repository - a collection of organized video processing utilities.

Key Features:
- Cross-platform support (Windows, Linux, macOS)
- UTF-8 encoding support for international file metadata
- Atomic operations using temporary files for safety
- Comprehensive logging with progress tracking
- Dry-run mode for testing without modifications
- Support for Windows UNC paths and common video formats

Requirements:
- MKVToolNix tools (mkvmerge executable)
- Python 3.6+

Usage:
    python scripts/audio/remove_non_english_audio.py <input_folder> [--mkv-tools-path <path>] [--dry-run]

Examples:
    # Windows (from repository root)
    python scripts/audio/remove_non_english_audio.py "C:\\Videos" --dry-run
    python scripts/audio/remove_non_english_audio.py "C:\\Videos"
    python scripts/audio/remove_non_english_audio.py "C:\\Videos" --mkv-tools-path "C:\\Program Files\\MKVToolNix"
    
    # Linux/Unix (from repository root)
    python scripts/audio/remove_non_english_audio.py "/home/user/videos" --dry-run
    python scripts/audio/remove_non_english_audio.py "/home/user/videos"
    python scripts/audio/remove_non_english_audio.py "/home/user/videos" --mkv-tools-path "/usr/local/bin"

Core Classes:
    AudioTrackRemover: Main processing class handling track analysis and removal
    MKVToolsError: Exception for MKVToolNix tool-related errors

Key Methods:
    - _run_command: Subprocess execution with UTF-8 encoding support
    - analyze_audio_tracks: Language detection and track categorization
    - remove_non_english_audio: Main file processing with atomic operations
    - process_folder: Batch processing with statistics tracking

IMPORTANT: Always backup your video files before running this script!
"""

import argparse
import os
import sys
import subprocess
import json
import shutil
import logging
import platform
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# Supported video file extensions
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.m4v', '.mov', '.wmv', '.flv', '.webm'}

# English language codes that we want to keep
ENGLISH_CODES = {'en', 'eng', 'english', 'en-US', 'en-GB'}


class MKVToolsError(Exception):
    """Exception raised when MKV tools are not found or fail."""
    pass


class AudioTrackRemover:
    """Handles the removal of non-English audio tracks from video files."""
    
    def __init__(self, mkv_tools_path: Optional[str] = None, dry_run: bool = False):
        self.mkv_tools_path = mkv_tools_path
        self.dry_run = dry_run
        self.mkvmerge_path = self._find_mkv_executable('mkvmerge')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mkv_audio_removal.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"MKV tools found: mkvmerge={self.mkvmerge_path}")
        if self.dry_run:
            self.logger.info("DRY RUN MODE: No files will be modified")
    
    def _find_mkv_executable(self, tool_name: str) -> str:
        """Find the MKV executable in the specified path or system PATH."""
        is_windows = platform.system() == "Windows"
        exe_name = f"{tool_name}.exe" if is_windows else tool_name
        
        # First check if mkv_tools_path was specified
        if self.mkv_tools_path:
            tool_path = os.path.join(self.mkv_tools_path, exe_name)
            if os.path.isfile(tool_path):
                return tool_path
            else:
                raise MKVToolsError(f"{exe_name} not found at {tool_path}")
        
        # Check system PATH
        tool_path = shutil.which(exe_name)
        if tool_path:
            return tool_path
        
        # Try common installation paths based on OS
        if is_windows:
            common_paths = [
                r"C:\Program Files\MKVToolNix",
                r"C:\Program Files (x86)\MKVToolNix",
                r"C:\MKVToolNix",
            ]
        else:
            # Linux/Unix common paths
            common_paths = [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/mkvtoolnix/bin",
                "/snap/bin",
                "/usr/local/mkvtoolnix/bin",
                "/home/linuxbrew/.linuxbrew/bin",
                os.path.expanduser("~/.local/bin"),
            ]
        
        for path in common_paths:
            tool_path = os.path.join(path, exe_name)
            if os.path.isfile(tool_path):
                return tool_path
        
        raise MKVToolsError(f"{exe_name} not found in PATH or common locations")
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            else:
                result = subprocess.run(cmd, check=True, encoding='utf-8')
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(cmd)}")
            self.logger.error(f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            raise
    
    def get_track_info(self, video_file: str) -> Dict:
        """Get track information from a video file using mkvmerge -J."""
        cmd = [self.mkvmerge_path, '-J', video_file]
        
        try:
            result = self._run_command(cmd)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get track info for {video_file}: {e}")
            return {}
    
    def analyze_audio_tracks(self, track_info: Dict) -> Tuple[List[Dict], List[int]]:
        """
        Analyze audio tracks and return English tracks info and non-English track IDs.
        
        Returns:
            Tuple of (english_tracks_info, non_english_track_ids)
        """
        english_tracks = []
        non_english_tracks = []
        
        if 'tracks' not in track_info:
            return english_tracks, non_english_tracks
        
        for track in track_info['tracks']:
            if track.get('type') == 'audio':
                track_id = track.get('id')
                if track_id is None:
                    continue
                
                # Check language property
                properties = track.get('properties', {})
                language = properties.get('language', '').lower()
                is_default = properties.get('default_track', False)
                
                track_info_dict = {
                    'id': track_id,
                    'language': language,
                    'is_default': is_default,
                    'properties': properties
                }
                
                # If no language specified, assume English (common default)
                if not language or language == 'und':
                    self.logger.warning(f"Track {track_id} has undefined language, assuming English")
                    english_tracks.append(track_info_dict)
                elif language in ENGLISH_CODES:
                    english_tracks.append(track_info_dict)
                else:
                    non_english_tracks.append(track_id)
                    self.logger.info(f"Found non-English audio track {track_id} with language: {language}")
        
        return english_tracks, non_english_tracks
    
    def remove_non_english_audio(self, video_file: str) -> bool:
        """
        Remove non-English audio tracks from a video file and set English as default.
        
        Returns:
            True if file was modified, False otherwise
        """
        self.logger.info(f"Processing: {video_file}")
        
        # Get track information
        track_info = self.get_track_info(video_file)
        if not track_info:
            self.logger.error(f"Could not get track info for {video_file}")
            return False
        
        english_tracks, non_english_tracks = self.analyze_audio_tracks(track_info)
        
        if not non_english_tracks and english_tracks and english_tracks[0].get('is_default', False):
            self.logger.info(f"No changes needed for {video_file} - only English tracks present and first is default")
            return False
        
        if not english_tracks:
            self.logger.warning(f"No English audio tracks found in {video_file}, skipping")
            return False
        
        # Check if we need to make changes
        needs_track_removal = len(non_english_tracks) > 0
        needs_default_change = english_tracks and not english_tracks[0].get('is_default', False)
        
        if not needs_track_removal and not needs_default_change:
            self.logger.info(f"No changes needed for {video_file}")
            return False
        
        changes_desc = []
        if needs_track_removal:
            changes_desc.append(f"remove {len(non_english_tracks)} non-English tracks")
        if needs_default_change:
            changes_desc.append("set English track as default")
        
        self.logger.info(f"Will {' and '.join(changes_desc)} for {video_file}")
        
        if self.dry_run:
            if needs_track_removal:
                self.logger.info(f"DRY RUN: Would remove tracks {non_english_tracks}")
            if needs_default_change:
                self.logger.info(f"DRY RUN: Would set track {english_tracks[0]['id']} as default")
            return True
        
        # Create temporary output file
        video_path = Path(video_file)
        temp_file = video_path.with_suffix('.temp' + video_path.suffix)
        
        try:
            # Build mkvmerge command
            cmd = [self.mkvmerge_path, '-o', str(temp_file)]
            
            # Set default audio track (first English track)
            if needs_default_change:
                cmd.extend(['--default-track', f"{english_tracks[0]['id']}:yes"])
                # Set all other audio tracks to not default
                for track in english_tracks[1:]:
                    cmd.extend(['--default-track', f"{track['id']}:no"])
            
            # Add audio track selection (exclude non-English tracks)
            if needs_track_removal:
                # Include only English tracks
                english_track_ids = [str(track['id']) for track in english_tracks]
                cmd.extend(['-a', ','.join(english_track_ids)])
            
            cmd.append(video_file)
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            self._run_command(cmd, capture_output=False)
            
            # Replace original with processed file
            video_path.unlink()  # Remove original
            temp_file.rename(video_path)  # Rename temp to original
            
            self.logger.info(f"Successfully processed {video_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process {video_file}: {e}")
            
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
                
            return False
    
    def find_video_files(self, root_folder: str) -> List[str]:
        """Recursively find all video files in the given folder."""
        video_files = []
        root_path = Path(root_folder)
        
        if not root_path.exists():
            raise FileNotFoundError(f"Folder not found: {root_folder}")
        
        if not root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root_folder}")
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                video_files.append(str(file_path))
        
        return sorted(video_files)
    
    def process_folder(self, folder_path: str) -> Dict[str, int]:
        """Process all video files in a folder and return statistics."""
        stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'error_files': 0
        }
        
        try:
            video_files = self.find_video_files(folder_path)
            stats['total_files'] = len(video_files)
            
            if not video_files:
                self.logger.info(f"No video files found in {folder_path}")
                return stats
            
            self.logger.info(f"Found {len(video_files)} video files to process")
            
            for video_file in video_files:
                try:
                    if self.remove_non_english_audio(video_file):
                        stats['processed_files'] += 1
                    else:
                        stats['skipped_files'] += 1
                except Exception as e:
                    self.logger.error(f"Error processing {video_file}: {e}")
                    stats['error_files'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error processing folder {folder_path}: {e}")
            stats['error_files'] = stats['total_files']
            return stats


def main():
    parser = argparse.ArgumentParser(
        description='Remove non-English audio tracks from video files using MKV tools',
        epilog='WARNING: This script modifies files directly. BACKUP YOUR FILES FIRST!'
    )
    
    parser.add_argument(
        'input_folder',
        help='Folder containing video files to process (supports subdirectories)'
    )
    
    parser.add_argument(
        '--mkv-tools-path',
        help='Path to MKVToolNix installation directory (optional if in PATH)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually modifying files'
    )
    
    args = parser.parse_args()
    
    if not args.dry_run:
        print("WARNING: This script will modify your video files directly!")
        print("Make sure you have backed up your files before proceeding.")
        response = input("Do you want to continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        remover = AudioTrackRemover(
            mkv_tools_path=args.mkv_tools_path,
            dry_run=args.dry_run
        )
        
        print(f"\nProcessing folder: {args.input_folder}")
        if args.dry_run:
            print("DRY RUN MODE: No files will be modified")
        
        stats = remover.process_folder(args.input_folder)
        
        print(f"\n=== Processing Complete ===")
        print(f"Total files found: {stats['total_files']}")
        print(f"Files processed: {stats['processed_files']}")
        print(f"Files skipped: {stats['skipped_files']}")
        print(f"Files with errors: {stats['error_files']}")
        
        if stats['error_files'] > 0:
            print(f"\nCheck mkv_audio_removal.log for detailed error information")
        
    except MKVToolsError as e:
        print(f"Error: {e}")
        print("\nMake sure MKVToolNix is installed and either:")
        print("1. Add it to your system PATH, or")
        print("2. Specify the path using --mkv-tools-path")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()