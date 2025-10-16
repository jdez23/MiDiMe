#!/usr/bin/env python3
"""
Test script for onset detection.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_processing.onset_detector import (
    detect_onsets,
    detect_onsets_with_strength,
    filter_weak_onsets,
    get_tempo,
    analyze_drum_pattern
)

def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_separator("Testing Onset Detection")
    
    # We'll use the drum stem we generated earlier
    # First, let's check if we have a drum stem from our previous tests
    drum_stem_path = None
    
    # Look for drum stems in processed directories
    search_dirs = [
        "storage/processed/sample",
        "storage/processed/service_test/stems"
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            # Find first drums.wav file
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file == "drums.wav":
                        drum_stem_path = os.path.join(root, file)
                        break
                if drum_stem_path:
                    break
    
    if not drum_stem_path or not os.path.exists(drum_stem_path):
        print("❌ No drum stem found. Please run test_audio_service.py first.")
        print("\nTo generate a drum stem, run:")
        print("  python test_audio_service.py")
        return 1
    
    print(f"Using drum stem: {drum_stem_path}")
    
    # Test 1: Basic onset detection
    print_separator("Test 1: Basic Onset Detection")
    try:
        onsets = detect_onsets(drum_stem_path)
        print(f"✅ Detected {len(onsets)} drum hits")
        print(f"\nFirst 10 hits (seconds):")
        for i, time in enumerate(onsets[:10]):
            print(f"  {i+1:2d}. {time:.3f}s")
        
        if len(onsets) > 10:
            print(f"  ... ({len(onsets) - 10} more hits)")
            
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 2: Onset detection with strength
    print_separator("Test 2: Onset Detection with Strength")
    try:
        onsets_with_strength = detect_onsets_with_strength(drum_stem_path)
        print(f"✅ Detected {len(onsets_with_strength)} hits with strength")
        print(f"\nFirst 10 hits (time, strength):")
        for i, (time, strength) in enumerate(onsets_with_strength[:10]):
            bar = '█' * int(strength * 20)
            print(f"  {i+1:2d}. {time:6.3f}s  {strength:.2f} {bar}")
        
        if len(onsets_with_strength) > 10:
            print(f"  ... ({len(onsets_with_strength) - 10} more hits)")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return 1
    
    # Test 3: Filter weak onsets
    print_separator("Test 3: Filtering Weak Onsets")
    try:
        strong_onsets = filter_weak_onsets(onsets_with_strength, min_strength=0.5)
        print(f"✅ Filtered: {len(onsets_with_strength)} → {len(strong_onsets)} hits")
        print(f"   (Removed {len(onsets_with_strength) - len(strong_onsets)} weak hits)")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return 1
    
    # Test 4: Tempo estimation
    print_separator("Test 4: Tempo Estimation")
    try:
        tempo = get_tempo(drum_stem_path)
        print(f"✅ Estimated tempo: {tempo:.1f} BPM")
        
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return 1
    
    # Test 5: Complete drum pattern analysis
    print_separator("Test 5: Complete Drum Pattern Analysis")
    try:
        pattern = analyze_drum_pattern(drum_stem_path, filter_weak=True)
        
        print(f"✅ Pattern Analysis Complete")
        print(f"\nResults:")
        print(f"  Duration:     {pattern['duration_seconds']:.2f} seconds")
        print(f"  Tempo:        {pattern['tempo_bpm']:.1f} BPM")
        print(f"  Total Hits:   {pattern['num_hits']}")
        print(f"  Hit Density:  {pattern['hit_density']:.1f} hits/second")
        print(f"\nOnset Times (first 15):")
        for i, time in enumerate(pattern['onset_times'][:15]):
            print(f"  {time:.3f}s", end="  ")
            if (i + 1) % 5 == 0:
                print()  # New line every 5
        print()
        
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print_separator("Test Summary")
    print("✅ All onset detection tests passed!")
    print(f"\nDrum stem analyzed: {drum_stem_path}")
    print(f"Found {pattern['num_hits']} drum hits at {pattern['tempo_bpm']:.0f} BPM")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
