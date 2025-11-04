#!/usr/bin/env python
"""
Test script for the /api/analyze endpoint.

This script tests the complete audio processing pipeline:
1. Upload audio file
2. Specify time range
3. Analyze drum pattern
4. Receive MIDI data
"""

import requests
import os
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
SAMPLE_AUDIO_PATH = "storage/test_samples/sample.wav"


def test_analyze_endpoint():
    """Test the /api/analyze endpoint with a sample audio file."""

    print("=" * 60)
    print("Testing /api/analyze endpoint")
    print("=" * 60)

    # Check if sample file exists
    if not os.path.exists(SAMPLE_AUDIO_PATH):
        print(f"❌ Sample audio file not found: {SAMPLE_AUDIO_PATH}")
        print("\nPlease provide a sample audio file (MP3, WAV, etc.)")
        return

    # Get file info
    file_size_mb = os.path.getsize(SAMPLE_AUDIO_PATH) / (1024 * 1024)
    print(f"\n📁 Sample file: {SAMPLE_AUDIO_PATH}")
    print(f"📊 File size: {file_size_mb:.2f} MB")

    # Prepare the request
    url = f"{API_BASE_URL}/analyze"

    # Test parameters - analyzing first 15 seconds for drums
    data = {
        'start_time': '0.0',      # Start at beginning
        'end_time': '15.0',       # 15 seconds (minimum duration)
        'instrument': 'drums'
    }

    print(f"\n🎵 Analysis parameters:")
    print(f"   - Start time: {data['start_time']}s")
    print(f"   - End time: {data['end_time']}s")
    print(f"   - Instrument: {data['instrument']}")

    # Open file and prepare multipart form data
    with open(SAMPLE_AUDIO_PATH, 'rb') as audio_file:
        files = {
            'audio_file': (Path(SAMPLE_AUDIO_PATH).name, audio_file, 'audio/wav')
        }

        print(f"\n🚀 Sending request to {url}...")
        print("⏳ This may take 10-30 seconds (Spleeter stem separation)...")

        try:
            response = requests.post(url, data=data, files=files, timeout=120)

            print(f"\n📥 Response status: {response.status_code}")

            # Parse response
            try:
                result = response.json()
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response:")
                print(response.text)
                return

            # Display results
            if response.status_code == 200 and result.get('status') == 'success':
                print("\n✅ Analysis successful!")
                print("\n" + "=" * 60)
                print("RESULTS")
                print("=" * 60)

                print(f"\n📋 Analysis ID: {result.get('analysis_id')}")
                print(f"⏱️  Duration: {result.get('duration')}s")
                print(f"🎹 Tempo: {result.get('tempo')} BPM")
                print(f"🎵 Time Signature: {result.get('time_signature')}")

                # MIDI data
                midi_data = result.get('midi_data', {})
                print(f"\n🥁 Drum Pattern:")
                print(f"   - Kicks: {len(midi_data.get('kick', []))} hits")
                print(f"   - Snares: {len(midi_data.get('snare', []))} hits")
                print(f"   - Hi-hats: {len(midi_data.get('hihat', []))} hits")

                # Show first few hits of each type
                print(f"\n📊 First few hit timings:")
                for drum_type in ['kick', 'snare', 'hihat']:
                    hits = midi_data.get(drum_type, [])
                    if hits:
                        first_hits = hits[:5]
                        print(f"   {drum_type.capitalize()}: {', '.join(f'{h:.3f}s' for h in first_hits)}")

                # Metadata
                metadata = result.get('metadata', {})
                print(f"\n📈 Metadata:")
                print(f"   - Total hits: {metadata.get('total_hits')}")
                print(f"   - Sample rate: {metadata.get('sample_rate')} Hz")
                print(f"   - Hit density: {metadata.get('hit_density', 0):.2f} hits/second")

                # Full response (pretty printed)
                print(f"\n📝 Full JSON Response:")
                print(json.dumps(result, indent=2))

            else:
                print(f"\n❌ Analysis failed:")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                if 'errors' in result:
                    print(f"   Errors: {result.get('errors')}")
                print(f"\n📝 Full response:")
                print(json.dumps(result, indent=2))

        except requests.exceptions.Timeout:
            print("\n❌ Request timed out (>120 seconds)")
            print("   This might indicate an issue with Spleeter or audio processing")

        except requests.exceptions.ConnectionError:
            print("\n❌ Connection error - is the Django server running?")
            print(f"   Make sure server is running at {API_BASE_URL}")

        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")


def test_health_check():
    """Test the health check endpoint first."""
    print("\n🏥 Testing health check endpoint...")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and reachable")
            return True
        else:
            print(f"⚠️  Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        return False


def main():
    """Run all tests."""
    print("\n🎯 MiDiMe API Test Suite")
    print("=" * 60)

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start it with:")
        print("   cd backend && python manage.py runserver")
        return

    # Test 2: Analyze endpoint
    test_analyze_endpoint()

    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
