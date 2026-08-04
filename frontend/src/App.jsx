import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import { streamChat, checkHealth } from './services/api';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  const abortControllerRef = useRef(null);

  // Load local sessions
  useEffect(() => {
    const storageKey = `agentic_rag_sessions_local`;
    try {
      const saved = localStorage.getItem(storageKey);
      setSessions(saved ? JSON.parse(saved) : []);
    } catch {
      setSessions([]);
    }
  }, []);

  // Sync sessions when updated
  useEffect(() => {
    const storageKey = `agentic_rag_sessions_local`;
    try {
      localStorage.setItem(storageKey, JSON.stringify(sessions));
    } catch (e) {
      console.error('Failed to save sessions:', e);
    }
  }, [sessions]);

  // Check health on mount
  useEffect(() => {
    const init = async () => {
      try {
        const health = await checkHealth();
        setIsOnline(health.status === 'ready');
      } catch {
        setIsOnline(false);
      }
    };
    init();
  }, []);

  // When active session changes, load its messages
  useEffect(() => {
    if (activeSessionId) {
      const current = sessions.find((s) => s.id === activeSessionId);
      if (current) {
        setMessages(current.messages || []);
      }
    } else {
      setMessages([]);
    }
  }, [activeSessionId, sessions]);

  // Create new session / Reset view
  const handleNewSession = () => {
    if (isLoading && abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setActiveSessionId(null);
    setMessages([]);
    setInput('');
  };

  // Delete session
  const handleDeleteSession = (sessionId) => {
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      setActiveSessionId(null);
      setMessages([]);
    }
  };

  // Clear current chat messages
  const handleClearChat = () => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }
    setMessages([]);
    setSessions((prev) =>
      prev.map((s) => (s.id === activeSessionId ? { ...s, messages: [] } : s))
    );
  };

  // Stop generation stream
  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  // Send message
  const handleSend = async (overridePrompt) => {
    const promptToSend = (overridePrompt || input).trim();
    if (!promptToSend || isLoading) return;

    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
      currentSessionId = `conv_${Date.now()}`;
      const newSession = {
        id: currentSessionId,
        title: promptToSend.slice(0, 32) + (promptToSend.length > 32 ? '...' : ''),
        createdAt: new Date().toISOString(),
        messages: [],
      };
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(currentSessionId);
    } else {
      setSessions((prev) =>
        prev.map((s) => {
          if (s.id === currentSessionId && (!s.messages || s.messages.length === 0)) {
            return {
              ...s,
              title: promptToSend.slice(0, 32) + (promptToSend.length > 32 ? '...' : ''),
            };
          }
          return s;
        })
      );
    }

    const userMessage = { role: 'user', content: promptToSend };
    const initialAssistantMessage = {
      id: null,
      role: 'assistant',
      content: '',
      tool_used: null,
      source_type: null,
      stepLabel: 'Analyzing context...',
      sources: [],
      latency_seconds: null,
    };

    const updatedMessages = [...messages, userMessage, initialAssistantMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    abortControllerRef.current = new AbortController();

    const historyPayload = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    let accumulatedContent = '';
    let messageId = null;

    await streamChat({
      question: promptToSend,
      conversationId: currentSessionId,
      chatHistory: historyPayload,
      signal: abortControllerRef.current.signal,
      onStep: (stepData) => {
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              stepLabel: stepData.label,
              tool_used: stepData.tool_used || next[lastIdx].tool_used,
            };
          }
          return next;
        });
      },
      onMetadata: (meta) => {
        messageId = meta.message_id || messageId;
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              id: meta.message_id || next[lastIdx].id,
              tool_used: meta.tool_used,
              source_type: meta.source_type,
              sources: meta.sources || [],
            };
          }
          return next;
        });
      },
      onToken: (token) => {
        accumulatedContent += token;
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              content: accumulatedContent,
            };
          }
          return next;
        });
      },
      onDone: (doneData) => {
        const finalAnswer = (doneData.full_answer || accumulatedContent || '').trim();
        const finalMsgId = doneData.message_id || messageId;
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              id: finalMsgId,
              content: finalAnswer,
              tool_used: doneData.tool_used || next[lastIdx].tool_used,
              source_type: doneData.source_type || next[lastIdx].source_type,
              latency_seconds: doneData.latency_seconds,
              stepLabel: null,
            };
          }
          return next;
        });

        // Persist to session
        setSessions((prevSessions) =>
          prevSessions.map((s) => {
            if (s.id === currentSessionId) {
              return {
                ...s,
                messages: [
                  ...(s.messages || []),
                  userMessage,
                  {
                    id: finalMsgId,
                    role: 'assistant',
                    content: finalAnswer,
                    tool_used: doneData.tool_used,
                    source_type: doneData.source_type,
                    latency_seconds: doneData.latency_seconds,
                    sources: nextLastAssistantSources(updatedMessages),
                  },
                ],
              };
            }
            return s;
          })
        );
        setIsLoading(false);
      },
      onError: (err) => {
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              content: `⚠️ ${err}`,
              stepLabel: null,
            };
          }
          return next;
        });
        setIsLoading(false);
      },
    });
  };

  const nextLastAssistantSources = (msgList) => {
    const last = msgList[msgList.length - 1];
    return last?.sources || [];
  };

  return (
    <div className="flex h-screen w-screen bg-[#000000] text-white overflow-hidden font-sans">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        user={{ username: 'Admin' }}
      />

      <ChatContainer
        messages={messages}
        input={input}
        setInput={setInput}
        onSend={() => handleSend()}
        onStop={handleStop}
        isLoading={isLoading}
        onClearChat={handleClearChat}
      />
    </div>
  );
}
