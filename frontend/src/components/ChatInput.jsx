import React, { useRef, useEffect, useState } from 'react';
import { Mic, AudioLines, ArrowUp, Square } from 'lucide-react';
import { transcribeVoice } from '../services/api';

export default function ChatInput({
  input,
  setInput,
  onSend,
  onStop,
  isLoading,
}) {
  const textareaRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [useFallback, setUseFallback] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  // Auto-resize textarea height smoothly
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
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
      if (useFallback && recognitionRef.current) {
        recognitionRef.current.stop();
      } else {
        mediaRecorderRef.current?.stop();
      }
      setIsRecording(false);
      return;
    }

    if (useFallback) {
      startBrowserSpeech();
      return;
    }

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
          setInput("Transcribing...");
          const transcript = await transcribeVoice(audioBlob);
          setInput(transcript);
        } catch (e) {
          console.warn("Cloud transcription failed, falling back to browser API:", e);
          setUseFallback(true);
          setInput("Cloud STT unavailable. Click mic to use browser STT.");
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied or error:", err);
    }
  };

  const startBrowserSpeech = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setInput("Web Speech API not supported in this browser.");
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = 'en-US';

    recognitionRef.current.onstart = () => {
      setIsRecording(true);
      setInput("Listening (Browser Fallback)...");
    };

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognitionRef.current.onerror = (event) => {
      console.error("Browser STT Error:", event.error);
      setInput("Browser STT failed.");
      setIsRecording(false);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current.start();
  };

  const hasText = Boolean(input.trim());

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      {/* Pill Capsule Container */}
      <div className={`relative flex items-center bg-[#212121] hover:bg-[#252525] focus-within:bg-[#212121] border border-neutral-800/80 rounded-full px-4 py-2 transition-all shadow-xl ${isRecording ? 'ring-2 ring-rose-500/50' : ''}`}>
        {/* Center: Textarea Input */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isRecording ? "Listening..." : "Ask anything"}
          rows={1}
          disabled={isLoading || isRecording}
          className="w-full bg-transparent text-white placeholder-neutral-400 text-[14px] px-1 py-1.5 focus:outline-none resize-none max-h-[180px] scrollbar-none leading-relaxed"
        />

        {/* Right Action Icons */}
        <div className="flex items-center gap-1.5 shrink-0 pl-2">
          {/* Mic Icon */}
          <button
            type="button"
            onClick={toggleRecording}
            className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
              isRecording ? 'text-white bg-rose-500 animate-pulse' : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'
            }`}
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>

          {/* Dynamic Action Button (Waveform / Arrow / Stop) */}
          {isLoading ? (
            <button
              type="button"
              onClick={onStop}
              className="w-8 h-8 rounded-full bg-neutral-200 hover:bg-white text-black flex items-center justify-center transition-all shrink-0"
              title="Stop generation"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          ) : hasText ? (
            <button
              type="button"
              onClick={onSend}
              className="w-8 h-8 rounded-full bg-white hover:bg-neutral-200 text-black flex items-center justify-center transition-all shadow-md shrink-0"
              title="Send message"
            >
              <ArrowUp className="w-4 h-4 stroke-[2.5]" />
            </button>
          ) : (
            <button
              type="button"
              className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center transition-all shadow-md shrink-0"
              title="Voice mode"
            >
              <AudioLines className="w-4 h-4 stroke-[2.2]" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
