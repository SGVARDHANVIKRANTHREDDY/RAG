'use client';
import { useState, useEffect, useRef } from 'react';
import { chatAPI, queryAPI } from '@/lib/api';
import MessageBubble from './MessageBubble';
import FileUpload from './FileUpload';
import VoiceInput from './VoiceInput';
import ThemeToggle from './ThemeToggle';

interface Message {
  id: number;
  role: string;
  content: string;
  sources?: any[];
}

export default function ChatInterface({ 
  chatId, 
  onRefreshChats 
}: { 
  chatId: number | null;
  onRefreshChats: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatId) {
      loadMessages();
    }
  }, [chatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    if (!chatId) return;
    try {
      const res = await chatAPI.getMessages(chatId);
      setMessages(res.data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Add user message to UI
    const tempUserMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
    };
    setMessages([...messages, tempUserMessage]);

    try {
      // Stream response
      const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '');
      const token = localStorage.getItem('access_token');
      const url = `${apiUrl}/api/v1/query/stream?query=${encodeURIComponent(userMessage)}${chatId ? `&chat_id=${chatId}` : ''}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedResponse = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6);
              if (data === '[DONE]') {
                // Finalize streaming
                const assistantMessage = {
                  id: Date.now() + 1,
                  role: 'assistant',
                  content: accumulatedResponse,
                };
                setMessages((prev) => [...prev, assistantMessage]);
                setStreamingMessage('');
                onRefreshChats();
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.token) {
                  accumulatedResponse += parsed.token;
                  setStreamingMessage(accumulatedResponse);
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (transcript: string) => {
    setInput(transcript);
  };

  if (!chatId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">Select a chat or create a new one</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700 bg-white dark:bg-gray-800">
        <h2 className="text-xl font-semibold">Chat</h2>
        <div className="flex gap-2">
          <FileUpload />
          <ThemeToggle />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {streamingMessage && (
          <MessageBubble 
            message={{ id: 0, role: 'assistant', content: streamingMessage }} 
            isStreaming 
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
            disabled={loading}
          />
          <VoiceInput onTranscript={handleVoiceInput} />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
