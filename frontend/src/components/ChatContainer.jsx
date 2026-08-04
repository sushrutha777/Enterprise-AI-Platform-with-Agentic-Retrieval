import React, { useRef, useEffect } from 'react';
import { 
  Menu, 
  Trash2, 
  Sparkles
} from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatContainer({
  messages = [],
  input,
  setInput,
  onSend,
  onStop,
  isLoading,
  onClearChat,
  onNewSession,
  isSidebarOpen,
  onToggleSidebar,
  isOnline = true,
}) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const isEmpty = messages.length === 0;

  return (
    <main className="flex-1 flex flex-col h-screen bg-[#000000] overflow-hidden relative selection:bg-amber-900 selection:text-amber-100">
      {/* Top Header Bar */}
      <header className="h-16 px-5 border-b border-[#141414] flex items-center justify-between shrink-0 bg-[#000000]/60 backdrop-blur-md z-30">
        {/* Left Side: Clean Hamburger Menu Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-xl text-neutral-300 hover:text-white hover:bg-[#1c1c1c] transition-all flex items-center justify-center border border-transparent hover:border-neutral-800"
            title={isSidebarOpen ? "Hide sidebar" : "Show sidebar"}
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Subtle App Branding */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#121212] border border-neutral-800/80 text-[12px] text-neutral-300 font-medium select-none">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Agentic RAG</span>
          </div>
        </div>

        {/* Right Side: Online Status */}
        <div className="flex items-center gap-3">
          {messages.length > 0 && (
            <button
              onClick={onClearChat}
              className="p-2 rounded-xl text-neutral-400 hover:text-rose-400 hover:bg-[#1a1a1a] transition-colors border border-transparent hover:border-neutral-800 text-xs flex items-center gap-1.5"
              title="Clear current messages"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}

          {/* Status Indicator */}
          {isOnline ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/40 text-[11px] text-emerald-400 font-medium select-none">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Online</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-950/40 border border-rose-800/40 text-[11px] text-rose-400 font-medium select-none" title="Backend is offline">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
              <span>Offline</span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      {isEmpty ? (
        /* Empty State: Golden Solar Amber Aesthetic */
        <div className="flex-1 flex flex-col justify-between relative overflow-hidden">
          {/* Ambient Golden Amber Solar Gradient Glow in lower half */}
          <div className="absolute inset-0 amber-gradient-bg pointer-events-none z-0" />

          {/* Center Greetings */}
          <div className="flex-1 flex flex-col items-center justify-center px-4 w-full max-w-xl mx-auto z-10 -mt-10">
            {/* Subtitle */}
            <p className="text-amber-200/80 text-sm md:text-[15px] font-normal tracking-wide mb-2.5 select-none">
              Hello, Explorer!
            </p>

            {/* Main Heading */}
            <h1 className="text-3xl sm:text-4xl md:text-[40px] font-medium text-white text-center leading-[1.2] tracking-tight mb-2 select-none">
              How Can I Help<br />You Today?
            </h1>
          </div>

          {/* Bottom Floating Input Container */}
          <div className="w-full pb-8 pt-4 px-4 z-10">
            <ChatInput
              input={input}
              setInput={setInput}
              onSend={onSend}
              onStop={onStop}
              isLoading={isLoading}
              isHeroTheme={true}
            />
          </div>
        </div>
      ) : (
        /* Active Chat View */
        <div className="flex-1 flex flex-col h-full overflow-hidden relative">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin z-10">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((msg, index) => (
                <ChatMessage
                  key={index}
                  message={msg}
                  isStreaming={isLoading && index === messages.length - 1 && msg.role === 'assistant'}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Bottom Sticky Input Container */}
          <div className="pb-6 pt-3 px-4 bg-gradient-to-t from-black via-black/95 to-transparent z-20">
            <ChatInput
              input={input}
              setInput={setInput}
              onSend={onSend}
              onStop={onStop}
              isLoading={isLoading}
              isHeroTheme={false}
            />
          </div>
        </div>
      )}
    </main>
  );
}
