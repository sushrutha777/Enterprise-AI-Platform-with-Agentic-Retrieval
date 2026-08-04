import React from 'react';
import { 
  SquarePen, 
  Trash2, 
  X,
  MessageSquare
} from 'lucide-react';

export default function Sidebar({
  isOpen = true,
  isMobile = false,
  onCloseMobile,
  sessions = [],
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}) {
  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`
          ${isMobile 
            ? 'fixed inset-y-0 left-0 z-50 w-72 bg-[#0d0d0d] shadow-2xl border-r border-[#222222]' 
            : 'relative bg-[#0d0d0d] border-r border-[#1a1a1a]'
          }
          h-screen flex flex-col shrink-0 select-none transition-all duration-300 ease-in-out
          ${!isMobile && (isOpen ? 'w-64 opacity-100' : 'w-0 opacity-0 overflow-hidden border-none pointer-events-none')}
          ${isMobile && (isOpen ? 'translate-x-0' : '-translate-x-full')}
        `}
      >
        {/* Top Header: New Chat & (Mobile Only) Close Button */}
        <div className="p-3 pt-3 flex items-center justify-between gap-2 border-b border-[#1c1c1c]/60">
          <button
            onClick={() => {
              onNewSession();
              if (isMobile) onCloseMobile();
            }}
            className="flex-1 flex items-center gap-2.5 py-2 px-3 rounded-xl bg-[#1c1c1c] hover:bg-[#252525] text-white text-[13px] font-medium transition-all group shadow-sm border border-neutral-800/60"
            title="Start a new chat"
          >
            <SquarePen className="w-4 h-4 text-neutral-300 group-hover:text-white" />
            <span>New chat</span>
          </button>

          {/* Close Button on Mobile Drawer */}
          {isMobile && (
            <button
              onClick={onCloseMobile}
              className="p-2 rounded-xl text-neutral-400 hover:text-white hover:bg-[#1c1c1c] transition-colors shrink-0"
              title="Close menu"
              aria-label="Close sidebar"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Chats History Section Header */}
        <div className="px-4 pt-3 pb-1 flex items-center justify-between">
          <span className="text-[11px] font-semibold tracking-wider uppercase text-neutral-500">Recent Chats</span>
          <span className="text-[10px] text-neutral-600 font-mono">{sessions.length}</span>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5 scrollbar-thin">
          {sessions.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-neutral-600 flex flex-col items-center gap-2">
              <MessageSquare className="w-5 h-5 text-neutral-700 stroke-[1.5]" />
              <span>No chat history yet</span>
            </div>
          ) : (
            sessions.map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <div
                  key={session.id}
                  onClick={() => {
                    onSelectSession(session.id);
                    if (isMobile) onCloseMobile();
                  }}
                  className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer text-[13px] transition-colors ${
                    isActive
                      ? 'bg-[#202020] text-white font-medium shadow-inner'
                      : 'text-neutral-300 hover:text-white hover:bg-[#161616]'
                  }`}
                >
                  <span className="truncate pr-2">{session.title || 'New chat'}</span>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-neutral-500 transition-opacity rounded"
                    title="Delete chat"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}
