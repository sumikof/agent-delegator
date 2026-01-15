from __future__ import annotations

from typing import Any, Dict, List
import tempfile
import os

from .base import Agent


class VoiceInterfaceAgent(Agent):
    def __init__(self, agent_id: str, name: str | None = None) -> None:
        super().__init__(agent_id, name)
        self.supported_formats = ["wav", "mp3", "ogg", "flac"]
        self.temp_dir = tempfile.mkdtemp(prefix="voice_interface_")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        operation = context.get("operation", "transcribe")
        result = {
            "status": "OK",
            "summary": f"Voice interface operation '{operation}' completed",
            "findings": [],
            "artifacts": [],
            "next_actions": [],
            "context": {}
        }
        
        try:
            if operation == "transcribe":
                return self._handle_transcription(context)
            elif operation == "synthesize":
                return self._handle_synthesis(context)
            elif operation == "process":
                return self._handle_audio_processing(context)
            else:
                result["status"] = "NG"
                result["summary"] = f"Unsupported voice operation: {operation}"
                result["findings"].append({
                    "severity": "ERROR",
                    "message": f"Operation '{operation}' is not supported",
                    "suggestion": "Use 'transcribe', 'synthesize', or 'process'"
                })
        
        except Exception as e:
            result["status"] = "NG"
            result["summary"] = f"Voice interface operation failed: {str(e)}"
            result["findings"].append({
                "severity": "ERROR", 
                "message": f"Voice interface error: {str(e)}",
                "suggestion": "Check audio data format and try again"
            })
        
        return result

    def _handle_transcription(self, context: Dict[str, Any]) -> Dict[str, Any]:
        audio_data = context.get("audio_data")
        language = context.get("language", "en-US")
        
        if not audio_data:
            return {
                "status": "NG",
                "summary": "No audio data provided for transcription",
                "findings": [{
                    "severity": "ERROR",
                    "message": "Missing audio_data in context",
                    "suggestion": "Provide audio data or file path"
                }],
                "artifacts": [],
                "next_actions": [],
                "context": {}
            }
        
        transcript = "This is a simulated transcription of the provided audio data. " \
                   "In a real implementation, this would contain the actual transcribed text " \
                   "from the speech recognition service."
        
        return {
            "status": "OK",
            "summary": f"Transcription completed for {language} audio",
            "findings": [],
            "artifacts": [{
                "path": "transcription.txt",
                "type": "doc",
                "desc": "Transcribed text from audio",
                "content": transcript
            }],
            "next_actions": ["review_transcription", "use_transcription_in_workflow"],
            "context": {
                "transcript": transcript,
                "language": language,
                "audio_format": self._detect_audio_format(audio_data)
            }
        }

    def _handle_synthesis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("text", "")
        language = context.get("language", "en-US")
        format = context.get("format", "wav")
        
        if not text:
            return {
                "status": "NG",
                "summary": "No text provided for speech synthesis",
                "findings": [{
                    "severity": "ERROR",
                    "message": "Missing text in context",
                    "suggestion": "Provide text to synthesize"
                }],
                "artifacts": [],
                "next_actions": [],
                "context": {}
            }
        
        if format not in self.supported_formats:
            return {
                "status": "NG",
                "summary": f"Unsupported audio format: {format}",
                "findings": [{
                    "severity": "ERROR",
                    "message": f"Format '{format}' is not supported",
                    "suggestion": f"Use one of: {', '.join(self.supported_formats)}"
                }],
                "artifacts": [],
                "next_actions": [],
                "context": {}
            }
        
        audio_file = self._simulate_speech_synthesis(text, language, format)
        
        return {
            "status": "OK",
            "summary": f"Speech synthesis completed for {language} text",
            "findings": [],
            "artifacts": [{
                "path": audio_file,
                "type": "audio",
                "desc": f"Synthesized speech in {format} format",
                "format": format,
                "language": language
            }],
            "next_actions": ["play_audio", "save_audio_file"],
            "context": {
                "audio_file": audio_file,
                "text_length": len(text),
                "format": format,
                "language": language
            }
        }

    def _handle_audio_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        audio_data = context.get("audio_data")
        operations = context.get("operations", [])
        
        if not audio_data:
            return {
                "status": "NG",
                "summary": "No audio data provided for processing",
                "findings": [{
                    "severity": "ERROR",
                    "message": "Missing audio_data in context",
                    "suggestion": "Provide audio data or file path"
                }],
                "artifacts": [],
                "next_actions": [],
                "context": {}
            }
        
        processed_file = self._simulate_audio_processing(audio_data, operations)
        
        return {
            "status": "OK",
            "summary": f"Audio processing completed with {len(operations)} operations",
            "findings": [],
            "artifacts": [{
                "path": processed_file,
                "type": "audio",
                "desc": "Processed audio file",
                "operations_applied": operations
            }],
            "next_actions": ["review_processed_audio", "use_processed_audio"],
            "context": {
                "processed_file": processed_file,
                "original_audio": audio_data,
                "operations": operations
            }
        }

    def _simulate_speech_synthesis(self, text: str, language: str, format: str) -> str:
        output_file = os.path.join(self.temp_dir, f"synthesis_{len(text[:20])}.{format}")
        with open(output_file, 'w') as f:
            f.write(f"Simulated {format.upper()} audio file for text: {text[:50]}...")
        return output_file

    def _simulate_audio_processing(self, audio_data: str, operations: List[str]) -> str:
        output_file = os.path.join(self.temp_dir, f"processed_{len(operations)}ops.wav")
        with open(output_file, 'w') as f:
            f.write(f"Simulated processed audio with operations: {', '.join(operations)}")
        return output_file

    def _detect_audio_format(self, audio_data: Any) -> str:
        if isinstance(audio_data, str):
            if audio_data.startswith("data:audio/") and "/" in audio_data:
                return audio_data.split("/")[-1].split(";")[0]
            elif os.path.exists(audio_data):
                return os.path.splitext(audio_data)[1][1:].lower()
        return "unknown"

    def cleanup(self) -> None:
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def __del__(self) -> None:
        self.cleanup()