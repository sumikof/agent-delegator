"""Unit tests for VoiceInterfaceAgent."""

import pytest
from orchestrator.agents.voice_interface import VoiceInterfaceAgent


def test_voice_interface_initialization():
    """Test that VoiceInterfaceAgent initializes correctly."""
    agent = VoiceInterfaceAgent("voice_interface")
    assert agent.id == "voice_interface"
    assert agent.name == "voice_interface"
    assert isinstance(agent.supported_formats, list)
    assert len(agent.supported_formats) > 0


def test_voice_interface_transcription():
    """Test voice transcription functionality."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    # Test transcription with sample audio data
    context = {
        "operation": "transcribe",
        "audio_data": "data:audio/wav;base64,sample_audio_data",
        "language": "en-US"
    }
    
    result = agent.run(context)
    
    assert result["status"] == "OK"
    assert "transcription" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "doc"
    assert "transcription" in result["artifacts"][0]["desc"]


def test_voice_interface_synthesis():
    """Test speech synthesis functionality."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    # Test synthesis with sample text
    context = {
        "operation": "synthesize",
        "text": "Hello, this is a test of the voice interface.",
        "language": "en-US",
        "format": "wav"
    }
    
    result = agent.run(context)
    
    assert result["status"] == "OK"
    assert "synthesis" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "audio"
    assert "synthesized" in result["artifacts"][0]["desc"]


def test_voice_interface_audio_processing():
    """Test audio processing functionality."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    # Test audio processing with sample operations
    context = {
        "operation": "process",
        "audio_data": "sample_audio.wav",
        "operations": ["normalize", "noise_reduction"]
    }
    
    result = agent.run(context)
    
    assert result["status"] == "OK"
    assert "processing" in result["summary"]
    assert len(result["artifacts"]) > 0
    assert result["artifacts"][0]["type"] == "audio"
    assert "processed" in result["artifacts"][0]["desc"]


def test_voice_interface_unsupported_operation():
    """Test handling of unsupported operations."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    context = {
        "operation": "unsupported_operation",
        "audio_data": "sample.wav"
    }
    
    result = agent.run(context)
    
    assert result["status"] == "NG"
    assert "unsupported" in result["summary"]
    assert len(result["findings"]) > 0
    assert result["findings"][0]["severity"] == "ERROR"


def test_voice_interface_missing_audio_data():
    """Test handling of missing audio data."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    context = {
        "operation": "transcribe"
        # Missing audio_data
    }
    
    result = agent.run(context)
    
    assert result["status"] == "NG"
    assert "no audio data" in result["summary"]
    assert len(result["findings"]) > 0


def test_voice_interface_unsupported_format():
    """Test handling of unsupported audio formats."""
    agent = VoiceInterfaceAgent("voice_interface")
    
    context = {
        "operation": "synthesize",
        "text": "Test text",
        "format": "unsupported_format"
    }
    
    result = agent.run(context)
    
    assert result["status"] == "NG"
    assert "unsupported" in result["summary"]
    assert len(result["findings"]) > 0


def test_voice_interface_cleanup():
    """Test that temporary files are cleaned up."""
    import os
    import tempfile
    
    agent = VoiceInterfaceAgent("voice_interface")
    temp_dir = agent.temp_dir
    
    # Verify temp directory was created
    assert os.path.exists(temp_dir)
    assert temp_dir.startswith("voice_interface_")
    
    # Clean up
    agent.cleanup()
    
    # Verify temp directory was removed
    assert not os.path.exists(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])