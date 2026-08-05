import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Copy, 
  Check, 
  Globe, 
  BookOpen, 
  FileText, 
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Clock
} from 'lucide-react';
import SourceCitations from './SourceCitations';
import { submitFeedback } from '../services/api';

export default function ChatMessage({ message, isStreaming = false }) {
  const [copied, setCopied] = useState(false);
  const [feedbackState, setFeedbackState] = useState(null);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedback = async (rating) => {
    if (!message.id) return;
    try {
      await submitFeedback(message.id, rating);
      setFeedbackState(rating === 1 ? 'liked' : 'disliked');
    } catch (e) {
      console.error('Feedback submission failed:', e);
    }
  };

  const renderToolBadge = () => {
    return null;

    if (tool === 'document_search' || tool === 'retriever' || tool === 'document') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <FileText className="w-3 h-3" />
          <span>Hybrid Retrieval</span>
        </span>
      );
    }

    if (tool.includes('wikipedia')) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <BookOpen className="w-3 h-3" />
          <span>Wikipedia Search</span>
        </span>
      );
    }

    if (tool.includes('web_search')) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Globe className="w-3 h-3" />
          <span>Web Search</span>
        </span>
      );
    }

    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-neutral-800 text-neutral-300 border border-neutral-700">
        <Sparkles className="w-3 h-3 text-neutral-400" />
        <span>{tool}</span>
      </span>
    );
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] bg-[#2f2f2f] text-white px-4 py-2.5 rounded-3xl text-[14px] leading-relaxed break-words shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-2 text-neutral-200">
      {/* Assistant metadata header */}
      <div className="flex items-center gap-2 flex-wrap text-xs">
        {renderToolBadge()}

        {message.stepLabel && isStreaming && (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-medium text-neutral-300 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
            {message.stepLabel}
          </span>
        )}
      </div>

      {/* Main Assistant Content */}
      <div className="prose prose-invert max-w-none text-neutral-100 text-[14px] leading-relaxed space-y-2">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline ? (
                <div className="relative group my-3">
                  <div className="absolute right-2 top-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                      }}
                      className="px-2 py-1 rounded bg-[#202020] hover:bg-[#2a2a2a] text-xs text-neutral-300 border border-neutral-700 flex items-center gap-1 shadow"
                    >
                      <Copy className="w-3 h-3" />
                      Copy
                    </button>
                  </div>
                  <pre className="!bg-[#141414] !border !border-neutral-800 !rounded-xl !p-3.5 overflow-x-auto text-xs">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              ) : (
                <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-neutral-200 font-mono text-xs" {...props}>
                  {children}
                </code>
              );
            },
            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
            ul: ({ children }) => <ul className="list-disc pl-5 my-2 space-y-1">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal pl-5 my-2 space-y-1">{children}</ol>,
            li: ({ children }) => <li className="text-neutral-200">{children}</li>,
            strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
          }}
        >
          {message.content || ''}
        </ReactMarkdown>
        {isStreaming && <span className="cursor-blink"></span>}
      </div>

      {/* Bottom actions (Copy & Feedback) */}
      {message.content && !isStreaming && (
        <div className="pt-1 flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] text-neutral-400 hover:text-white hover:bg-neutral-800/60 transition-colors"
            title="Copy response"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          {message.id && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => handleFeedback(1)}
                className={`p-1 rounded text-xs transition-colors ${
                  feedbackState === 'liked' ? 'text-white bg-neutral-800' : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
                }`}
                title="Good response"
              >
                <ThumbsUp className="w-3 h-3" />
              </button>
              <button
                onClick={() => handleFeedback(-1)}
                className={`p-1 rounded text-xs transition-colors ${
                  feedbackState === 'disliked' ? 'text-rose-400 bg-neutral-800' : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
                }`}
                title="Poor response"
              >
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
