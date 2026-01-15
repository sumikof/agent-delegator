#!/usr/bin/env python3
"""Simple test script for VoiceInterfaceAgent."""

import sys
import os

# Add the workspace to Python path
sys.path.insert(0, '/workspace')

from orchestrator.agents.voice_interface import VoiceInterfaceAgent


def test_voice_interface():
    """Test VoiceInterfaceAgent functionality."""
    print("Testing VoiceInterfaceAgent...")
    
    # Test 1: Initialization
    print("\n1. Testing initialization...")
    agent = VoiceInterfaceAgent("voice_interface")
    assert agent.id == "voice_interface"
    assert agent.name == "voice_interface"
    assert isinstance(agent.supported_formats, list)
    assert len(agent.supported_formats) > 0
    print("✓ Initialization successful")
    
    # Test 2: Transcription
    print("\n2. Testing transcription...")
    context = {
        "operation": "transcribe",
        "audio_data": "data:audio/wav;base64,sample_audio_data",
        "language": "en-US"
    }
    result = agent.run(context)
    assert result["status"] == "OK"
    assert "Transcription completed" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "doc"
    print("✓ Transcription successful")
    
    # Test 3: Synthesis
    print("\n3. Testing speech synthesis...")
    context = {
        "operation": "synthesize",
        "text": "Hello, this is a test of the voice interface.",
        "language": "en-US",
        "format": "wav"
    }
    result = agent.run(context)
    assert result["status"] == "OK"
    assert "Speech synthesis completed" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "audio"
    print("✓ Speech synthesis successful")
    
    # Test 4: Audio processing
    print("\n4. Testing audio processing...")
    context = {
        "operation": "process",
        "audio_data": "sample_audio.wav",
        "operations": ["normalize", "noise_reduction"]
    }
    result = agent.run(context)
    assert result["status"] == "OK"
    assert "Audio processing completed" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "audio"
    print("✓ Audio processing successful")
    
    # Test 5: Unsupported operation
    print("\n5. Testing unsupported operation...")
    context = {
        "operation": "unsupported_operation",
        "audio_data": "sample.wav"
    }
    result = agent.run(context)
    assert result["status"] == "NG"
    assert "unsupported" in result["summary"]
    assert len(result["findings"]) > 0
    print("✓ Unsupported operation handled correctly")
    
    # Test 6: Missing audio data
    print("\n6. Testing missing audio data...")
    context = {
        "operation": "transcribe"
        # Missing audio_data
    }
    result = agent.run(context)
    assert result["status"] == "NG"
    assert "No audio data provided" in result["summary"]
    print("✓ Missing audio data handled correctly")
    
    # Test 7: Unsupported format
    print("\n7. Testing unsupported format...")
    context = {
        "operation": "synthesize",
        "text": "Test text",
        "format": "unsupported_format"
    }
    result = agent.run(context)
    assert result["status"] == "NG"
    assert "unsupported" in result["summary"]
    print("✓ Unsupported format handled correctly")
    
    # Test 8: Cleanup
    print("\n8. Testing cleanup...")
    temp_dir = agent.temp_dir
    assert os.path.exists(temp_dir)
    agent.cleanup()
    assert not os.path.exists(temp_dir)
    print("✓ Cleanup successful")
    
    print("\n🎉 All tests passed! VoiceInterfaceAgent is working correctly.")


if __name__ == "__main__":
    try:
        test_voice_interface()
        print("\n✅ Voice interface implementation completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)