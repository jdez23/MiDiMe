#!/usr/bin/env python3
"""
Test script for stem separator.
"""

import sys
import os

# Add audio_processing to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_processing.stem_separator import separate_stems

def main():
    # Paths
    audio_path = "storage/test_samples/sample.wav"
    output_dir = "storage/processed"
    
    print(f"Testing stem separation...")
    print(f"Input: {audio_path}")
    print(f"Output: {output_dir}")
    print("-" * 60)
    
    try:
        # Separate stems
        stem_paths = separate_stems(audio_path, output_dir)
        
        print("\n✅ Stem separation successful!")
        print("\nGenerated stems:")
        for stem_name, stem_path in stem_paths.items():
            file_size = os.path.getsize(stem_path) / (1024 * 1024)  # MB
            print(f"  - {stem_name:8s}: {stem_path} ({file_size:.2f} MB)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Stem separation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
