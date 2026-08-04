import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatContainer({
  messages = [],
  input,
  setInput,
  onSend,
  onStop,
  isLoading,
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
    <main className="flex-1 flex flex-col h-screen bg-[#000000] overflow-hidden relative">
      {isEmpty ? (
        /* Empty State: Pure clean minimalist view */
        <div className="flex-1 flex flex-col items-center justify-center px-4 w-full max-w-3xl mx-auto">
          <h1 className="text-2xl md:text-[28px] font-normal text-white tracking-tight mb-7 text-center">
            What's on the agenda today?
          </h1>

          <div className="w-full">
            <ChatInput
              input={input}
              setInput={setInput}
              onSend={onSend}
              onStop={onStop}
              isLoading={isLoading}
            />
          </div>
        </div>
      ) : (
        /* Active Chat View */
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin">
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

          {/* Bottom Sticky Input */}
          <div className="pb-6 pt-2 bg-gradient-to-t from-black via-black/90 to-transparent">
            <ChatInput
              input={input}
              setInput={setInput}
              onSend={onSend}
              onStop={onStop}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}
    </main>
  );
}
