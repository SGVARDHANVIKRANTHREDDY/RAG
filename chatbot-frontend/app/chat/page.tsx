'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import ChatInterface from '@/components/ChatInterface';
import Sidebar from '@/components/Sidebar';
import { chatAPI } from '@/lib/api';

interface Chat {
  id: number;
  title: string;
  created_at: string;
  space_id?: string;
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadChats();
  }, [router]);

  const loadChats = async () => {
    try {
      const res = await chatAPI.listChats();
      setChats(res.data);
      if (res.data.length > 0 && !currentChatId) {
        setCurrentChatId(res.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await chatAPI.createChat('New Chat');
      setChats([res.data, ...chats]);
      setCurrentChatId(res.data.id);
    } catch (error) {
      console.error('Failed to create chat:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      <Sidebar 
        chats={chats} 
        currentChatId={currentChatId} 
        onSelectChat={setCurrentChatId}
        onNewChat={handleNewChat}
        onRefresh={loadChats}
      />
      <ChatInterface 
        chatId={currentChatId} 
        chats={chats}
        onRefreshChats={loadChats} 
      />
    </div>
  );
}
