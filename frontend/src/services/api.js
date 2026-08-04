/**
 * Enterprise API Service for Agentic RAG Platform
 */

const API_BASE = '/api/v1';

/**
 * Stream chat response using Server-Sent Events (SSE)
 */
export async function streamChat({
  question,
  conversationId,
  chatHistory = [],
  onStep,
  onMetadata,
  onToken,
  onDone,
  onError,
  signal,
}) {
  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
        chat_history: chatHistory,
      }),
      signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error (${response.status}): ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let currentEvent = 'message';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.replace(/^event:\s*/, '');
          continue;
        }

        if (trimmed.startsWith('data:')) {
          const rawData = trimmed.replace(/^data:\s*/, '');
          try {
            const parsed = JSON.parse(rawData);

            switch (currentEvent) {
              case 'step':
                if (onStep) onStep(parsed);
                break;
              case 'metadata':
                if (onMetadata) onMetadata(parsed);
                break;
              case 'token':
                if (onToken) onToken(parsed.token || parsed.text || '');
                break;
              case 'done':
                if (onDone) onDone(parsed);
                break;
              case 'error':
                if (onError) onError(parsed.error || parsed.message || 'Error occurred');
                break;
              default:
                if (parsed.token && onToken) onToken(parsed.token);
                break;
            }
          } catch {
            if (currentEvent === 'token' && onToken) {
              onToken(rawData);
            }
          }
        }
      }
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('Stream aborted by user');
      return;
    }
    console.error('Chat stream error:', err);
    if (onError) onError(err.message || 'Connection lost');
  }
}

/**
 * Check backend health
 */
export async function checkHealth() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);
  try {
    const response = await fetch(`${API_BASE}/health/ready`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!response.ok) throw new Error('Backend offline');
    return await response.json();
  } catch (e) {
    clearTimeout(timeoutId);
    throw e;
  }
}

/**
 * Transcribe Voice to Text
 */
export async function transcribeVoice(audioBlob) {
  const formData = new FormData();
  formData.append('file', audioBlob);

  const response = await fetch(`${API_BASE}/voice/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Transcription failed');
  }

  const data = await response.json();
  return data.transcript;
}

/**
 * Submit thumbs up/down feedback
 */
export async function submitFeedback(messageId, rating, comment = '') {
  try {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: messageId, rating, comment }),
    });
    if (!response.ok) return { status: 'ignored' };
    return response.json();
  } catch {
    return { status: 'offline' };
  }
}

