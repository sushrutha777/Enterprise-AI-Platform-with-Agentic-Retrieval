import React, { useState } from 'react';
import { FileText, ExternalLink, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

export default function SourceCitations({ sources = [] }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-white/10">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors py-1 px-2.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20"
      >
        <BookOpen className="w-3.5 h-3.5" />
        <span>{sources.length} Referenced Source{sources.length > 1 ? 's' : ''}</span>
        {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {isExpanded && (
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2.5 animate-fadeIn">
          {sources.map((src, index) => (
            <div
              key={index}
              onClick={() => setSelectedSource(selectedSource === index ? null : index)}
              className={`p-3 rounded-xl border transition-all cursor-pointer text-left ${
                selectedSource === index
                  ? 'bg-indigo-950/40 border-indigo-500/40 ring-1 ring-indigo-500/30'
                  : 'bg-white/[0.02] hover:bg-white/[0.05] border-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 overflow-hidden">
                  <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span className="text-xs font-semibold text-slate-200 truncate">
                    {src.title || `Source ${index + 1}`}
                  </span>
                </div>
                {src.page && (
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-slate-300 shrink-0">
                    p.{src.page}
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {src.snippet}
              </p>

              {selectedSource === index && src.snippet.length > 150 && (
                <div className="mt-2.5 pt-2 border-t border-white/10 text-xs text-slate-300 leading-relaxed max-h-48 overflow-y-auto">
                  {src.snippet}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
