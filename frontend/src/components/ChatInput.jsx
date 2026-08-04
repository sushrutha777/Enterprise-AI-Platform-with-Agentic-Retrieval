import React, { useRef, useEffect, useState } from 'react';
import { Mic, AudioLines, ArrowUp, Square } from 'lucide-react';
import { transcribeVoice } from '../services/api';

export default function ChatInput({
  input,
  setInput,
  onSend,
  onStop,
  isLoading,
  isHeroTheme = false,
}) {
  const textareaRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  // Auto-resize textarea height smoothly
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && input.trim()) {
        onSend();
      }
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {}
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop();
        } catch {}
      }
      setIsRecording(false);
      return;
    }

    // Primary: Web Speech API for instant browser speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          setIsRecording(true);
        };

        recognition.onresult = (event) => {
          let currentText = '';
          for (let i = 0; i < event.results.length; i++) {
            currentText += event.results[i][0].transcript;
          }
          setInput(currentText);
        };

        recognition.onerror = (event) => {
          console.warn("Browser Speech Recognition error:", event.error);
          setIsRecording(false);
        };

        recognition.onend = () => {
          setIsRecording(false);
        };

        recognition.start();
        return;
      } catch (e) {
        console.warn("Direct Speech Recognition failed, falling back to MediaRecorder:", e);
      }
    }

    // Secondary Fallback: MediaRecorder -> Backend STT API
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        try {
          const transcript = await transcribeVoice(audioBlob);
          if (transcript) setInput(transcript);
        } catch (e) {
          console.warn("Backend STT error:", e);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access error:", err);
    }
  };

  const hasText = Boolean(input.trim());

  return (
    <div className="w-full max-w-xl mx-auto">
      {/* Pill Capsule Container */}
      <div
        className={`relative flex items-center rounded-full px-4 py-2 transition-all duration-300 shadow-2xl ${
          isHeroTheme
            ? 'bg-[#2b1807]/90 hover:bg-[#3d230b]/95 focus-within:bg-[#3d230b] border border-[#854508]/70 focus-within:border-amber-500/80 backdrop-blur-xl'
            : 'bg-[#181818] hover:bg-[#202020] focus-within:bg-[#202020] border border-neutral-800 focus-within:border-neutral-700'
        } ${isRecording ? 'ring-2 ring-amber-500' : ''}`}
      >
        {/* Input Textarea */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isRecording ? "Listening..." : "Ask anything..."}
          rows={1}
          disabled={isLoading || isRecording}
          className="w-full bg-transparent text-white placeholder-amber-200/50 text-[15px] px-2 py-1.5 focus:outline-none resize-none max-h-[160px] scrollbar-none leading-relaxed"
        />

        {/* Right Action Controls */}
        <div className="flex items-center gap-1.5 shrink-0 pl-2">
          {/* Dynamic Action Button (Waveform / Arrow / Stop / Mic) */}
          {isLoading ? (
            <button
              type="button"
              onClick={onStop}
              className="w-9 h-9 rounded-full bg-amber-500 hover:bg-amber-400 text-black flex items-center justify-center transition-all shrink-0 shadow-lg"
              title="Stop generation"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          ) : hasText ? (
            <button
              type="button"
              onClick={() => onSend()}
              className="w-9 h-9 rounded-full bg-amber-500 hover:bg-amber-400 text-black flex items-center justify-center transition-all shadow-lg shrink-0 group"
              title="Send message"
            >
              <ArrowUp className="w-4 h-4 stroke-[2.5] group-hover:scale-110 transition-transform" />
            </button>
          ) : (
            <button
              type="button"
              onClick={toggleRecording}
              className={`w-9 h-9 rounded-full flex items-center justify-center transition-all shrink-0 ${
                isRecording
                  ? 'bg-amber-500 text-black animate-pulse shadow-lg'
                  : 'text-amber-200/70 hover:text-white hover:bg-amber-950/40'
              }`}
              title="Voice mode / Microphone"
            >
              {isRecording ? (
                <Mic className="w-4 h-4" />
              ) : (
                <AudioLines className="w-5 h-5 text-amber-300 hover:text-white stroke-[2.2] transition-colors" />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
