#!/usr/bin/env python3
"""
Test script for integrated audio processing service.

This tests the complete workflow: validation → trimming → stem separation → cleanup
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_processing import (
    process_audio_snippet,
    get_drum_pattern,
    AudioProcessingResult
)

def print_separator(title):
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(result: AudioProcessingResult):
    """Print processing result in a readable format."""
    if result.success:
        print("✅ Processing SUCCESSFUL!")
        print("\nMetadata:")
        for key, value in result.metadata.items():
            print(f"  - {key}: {value}")
        
        print("\nGenerated Stems:")
        for stem_name, stem_path in result.stem_paths.items():
            if os.path.exists(stem_path):
                size_mb = os.path.getsize(stem_path) / (1024 * 1024)
                print(f"  - {stem_name:10s}: {stem_path} ({size_mb:.2f} MB)")
            else:
                print(f"  - {stem_name:10s}: {stem_path} (FILE MISSING!)")
    else:
        print("❌ Processing FAILED!")
        print(f"Error: {result.error}")

def main():
    print_separator("Testing Integrated Audio Processing Service")
    
    # Test configuration
    audio_path = "storage/test_samples/sample.wav"
    output_dir = "storage/processed/service_test"
    
    # Test 1: Process audio snippet with all features
    print_separator("Test 1: Full Workflow (trim + stem separation)")
    print(f"Input: {audio_path}")
    print(f"Time range: 3.0s - 18.0s (15 seconds)")
    print(f"Output: {output_dir}")
    
    try:
        result = process_audio_snippet(
            audio_path=audio_path,
            start_time_seconds=3.0,
            end_time_seconds=18.0,
            output_base_dir=output_dir,
            extract_stems=True,
            cleanup_after=False  # Keep files for inspection
        )
        
        print_result(result)
        
        if not result.success:
            print("\n❌ Test 1 failed")
            return 1
            
    except Exception as e:
        print(f"❌ Test 1 failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 2: Use convenience function for drum extraction
    print_separator("Test 2: Drum Pattern Extraction (convenience function)")
    print(f"Using get_drum_pattern()...")
    
    try:
        drum_result = get_drum_pattern(
            audio_path=audio_path,
            start_time_seconds=3.0,
            end_time_seconds=18.0,
            output_base_dir=output_dir
        )
        
        print_result(drum_result)
        
        if not drum_result.success:
            print("\n❌ Test 2 failed")
            return 1
        
        # Verify drum stem exists
        if 'drums' in drum_result.stem_paths:
            drum_path = drum_result.stem_paths['drums']
            if os.path.exists(drum_path):
                print(f"\n✅ Drum stem verified: {drum_path}")
            else:
                print(f"\n❌ Drum stem missing: {drum_path}")
                return 1
        
    except Exception as e:
        print(f"❌ Test 2 failed with exception: {e}")
        return 1
    
    # Test 3: Validation errors
    print_separator("Test 3: Error Handling")
    
    # Test 3a: Invalid time range
    print("\n3a. Testing invalid time range (start > end)...")
    result = process_audio_snippet(
        audio_path=audio_path,
        start_time_seconds=18.0,
        end_time_seconds=3.0,
        output_base_dir=output_dir
    )
    
    if not result.success and "Trimming failed" in result.error:
        print(f"✅ Correctly rejected: {result.error}")
    else:
        print(f"❌ Should have failed with trimming error")
        return 1
    
    # Test 3b: Duration too short
    print("\n3b. Testing duration too short (< 15 seconds)...")
    result = process_audio_snippet(
        audio_path=audio_path,
        start_time_seconds=0.0,
        end_time_seconds=10.0,
        output_base_dir=output_dir
    )
    
    if not result.success and ("too short" in result.error or "Trimming failed" in result.error):
        print(f"✅ Correctly rejected: {result.error}")
    else:
        print(f"❌ Should have failed with duration error")
        return 1
    
    # Test 3c: Non-existent file
    print("\n3c. Testing non-existent file...")
    result = process_audio_snippet(
        audio_path="nonexistent.wav",
        start_time_seconds=0.0,
        end_time_seconds=15.0,
        output_base_dir=output_dir
    )
    
    if not result.success and "Validation failed" in result.error:
        print(f"✅ Correctly rejected: {result.error}")
    else:
        print(f"❌ Should have failed with validation error")
        return 1
    
    # Summary
    print_separator("Test Summary")
    print("✅ All tests passed!")
    print(f"\nGenerated files in: {output_dir}")
    print("\nTo inspect the stems:")
    print(f"  cd {output_dir}/stems")
    print("  ls -lh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
