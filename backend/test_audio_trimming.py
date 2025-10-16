#!/usr/bin/env python3
"""
Test script for audio trimming utilities.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_processing.utils import (
    trim_audio,
    get_audio_info,
    validate_audio_file,
    convert_to_wav
)

def main():
    print("=" * 60)
    print("Testing Audio Trimming Utilities")
    print("=" * 60)
    
    # Paths
    audio_path = "storage/test_samples/sample.wav"
    output_dir = "storage/processed/trimmed"
    
    # Test 1: Get audio info
    print("\n1. Getting audio information...")
    print("-" * 60)
    try:
        info = get_audio_info(audio_path)
        audio_duration = info['duration_seconds']
        print(f"✅ Audio Info:")
        print(f"   Duration: {audio_duration:.2f} seconds")
        print(f"   Sample Rate: {info['sample_rate']} Hz")
        print(f"   Channels: {info['channels']}")
        print(f"   Format: {info['format']}")
        print(f"   File Size: {info['file_size_mb']} MB")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1
    
    # Test 2: Validate audio file
    print("\n2. Validating audio file...")
    print("-" * 60)
    is_valid, error_msg = validate_audio_file(audio_path)
    if is_valid:
        print(f"✅ Audio file is valid")
    else:
        print(f"❌ Invalid audio file: {error_msg}")
        return 1
    
    # Determine safe trim range based on actual duration
    # Trim last 15 seconds (or full duration if < 15s)
    if audio_duration >= 15:
        start_time = max(0, audio_duration - 15)
        end_time = audio_duration
    else:
        print(f"⚠️  Audio is shorter than 15 seconds, cannot trim to valid range")
        return 1
    
    # Test 3: Trim audio (last 15 seconds)
    print(f"\n3. Trimming audio ({start_time:.1f}-{end_time:.1f} seconds)...")
    print("-" * 60)
    try:
        output_path = os.path.join(output_dir, f"sample_{int(start_time)}_{int(end_time)}.wav")
        trimmed_path = trim_audio(
            audio_path,
            output_path,
            start_time_seconds=start_time,
            end_time_seconds=end_time
        )
        
        # Get trimmed audio info
        trimmed_info = get_audio_info(trimmed_path)
        print(f"✅ Trimmed audio created: {trimmed_path}")
        print(f"   Duration: {trimmed_info['duration_seconds']:.2f} seconds")
        print(f"   File Size: {trimmed_info['file_size_mb']} MB")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 4: Test validation errors
    print("\n4. Testing validation errors...")
    print("-" * 60)
    
    # Test: Duration too short (< 15 seconds)
    try:
        output_path = os.path.join(output_dir, "sample_too_short.wav")
        trim_audio(audio_path, output_path, 0, 10)
        print("❌ Should have failed: duration too short")
        return 1
    except ValueError as e:
        print(f"✅ Correctly rejected short duration: {str(e)[:60]}...")
    
    # Test: End time exceeds duration
    try:
        output_path = os.path.join(output_dir, "sample_exceeds.wav")
        trim_audio(audio_path, output_path, 0, audio_duration + 10)
        print("❌ Should have failed: end time exceeds duration")
        return 1
    except (ValueError, RuntimeError) as e:
        print(f"✅ Correctly rejected time beyond duration: {str(e)[:60]}...")
    
    # Test: Invalid time range (start > end)
    try:
        output_path = os.path.join(output_dir, "sample_invalid.wav")
        trim_audio(audio_path, output_path, 10, 5)
        print("❌ Should have failed: invalid time range")
        return 1
    except ValueError as e:
        print(f"✅ Correctly rejected invalid time range: {str(e)[:60]}...")
    
    # Test: Negative start time
    try:
        output_path = os.path.join(output_dir, "sample_negative.wav")
        trim_audio(audio_path, output_path, -5, 15)
        print("❌ Should have failed: negative start time")
        return 1
    except ValueError as e:
        print(f"✅ Correctly rejected negative start time: {str(e)[:60]}...")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
