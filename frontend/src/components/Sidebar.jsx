import React, { useState, useRef, useEffect } from 'react';
import { 
  SquarePen, 
  Trash2, 
  LogOut, 
  MoreHorizontal
} from 'lucide-react';

export default function Sidebar({
  sessions = [],
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  user,
}) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const username = user?.username || 'SUSHRUTHA';
  const userInitials = (username || 'SU').slice(0, 2).toUpperCase();

  // Close menu on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <aside className="w-64 h-screen bg-[#000000] border-r border-[#171717] flex flex-col shrink-0 select-none">
      {/* Top Header / New Chat Button */}
      <div className="p-3 pt-3">
        <button
          onClick={onNewSession}
          className="w-full flex items-center gap-2.5 py-2.5 px-3.5 rounded-xl bg-[#1a1a1a] hover:bg-[#222222] text-white text-[13px] font-medium transition-all group shadow-sm"
        >
          <SquarePen className="w-4 h-4 text-neutral-300 group-hover:text-white" />
          <span>New chat</span>
        </button>
      </div>

      {/* Chats Section Header */}
      <div className="px-4 pt-3 pb-1 flex items-center justify-between">
        <span className="text-[12px] font-semibold text-neutral-400">Chats</span>
      </div>

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5 scrollbar-thin">
        {sessions.length === 0 ? null : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <div
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer text-[13px] transition-colors ${
                  isActive
                    ? 'bg-[#202020] text-white font-medium'
                    : 'text-neutral-300 hover:text-white hover:bg-[#151515]'
                }`}
              >
                <span className="truncate pr-2">{session.title || 'New chat'}</span>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-neutral-500 transition-opacity"
                  title="Delete chat"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Profile Card */}
      <div className="p-3 border-t border-[#171717] bg-[#000000] relative" ref={menuRef}>
        {/* User Account Popover */}
        {isMenuOpen && (
          <div className="absolute bottom-16 left-3 right-3 bg-[#181818] border border-neutral-800 rounded-2xl p-2 shadow-2xl z-50 animate-fadeIn space-y-1">
            <div className="px-3 py-2 border-b border-neutral-800/80">
              <p className="text-[11px] font-medium text-neutral-400">Signed in as</p>
              <p className="text-[13px] font-bold text-white uppercase truncate">{username}</p>
            </div>
          </div>
        )}

        {/* Profile trigger card */}
        <div
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="flex items-center justify-between p-2 rounded-xl hover:bg-[#151515] cursor-pointer transition-colors group"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-[#1c1c1c] border border-neutral-700 flex items-center justify-center text-[10px] font-bold text-neutral-200 shrink-0">
              {userInitials}
            </div>
            <div className="truncate text-left">
              <div className="text-[12px] font-semibold text-white tracking-wide uppercase truncate">
                {username}
              </div>
              <div className="text-[10px] text-neutral-400 font-normal">
                Go
              </div>
            </div>
          </div>

          <div className="p-1 text-neutral-400 group-hover:text-white transition-colors">
            <MoreHorizontal className="w-4 h-4" />
          </div>
        </div>
      </div>
    </aside>
  );
}
