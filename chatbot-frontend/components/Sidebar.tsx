'use client';
import { useRouter } from 'next/navigation';
import { clearTokens } from '@/lib/auth';
import { chatAPI } from '@/lib/api';

interface Chat {
  id: number;
  title: string;
  created_at: string;
  space_id?: string;
}

export default function Sidebar({
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onRefresh,
}: {
  chats: Chat[];
  currentChatId: number | null;
  onSelectChat: (id: number) => void;
  onNewChat: () => void;
  onRefresh: () => void;
}) {
  const router = useRouter();

  const handleLogout = () => {
    clearTokens();
    router.push('/login');
  };

  const handleDeleteChat = async (chatId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this chat?')) {
      try {
        await chatAPI.deleteChat(chatId);
        onRefresh();
      } catch (error) {
        console.error('Failed to delete chat:', error);
      }
    }
  };

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewChat}
          className="w-full py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`p-3 mb-2 rounded-lg cursor-pointer hover:bg-gray-700 flex justify-between items-center ${
              currentChatId === chat.id ? 'bg-gray-700' : ''
            }`}
          >
            <span className="truncate flex-1">{chat.title}</span>
            <button
              onClick={(e) => handleDeleteChat(chat.id, e)}
              className="ml-2 text-red-400 hover:text-red-300"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={handleLogout}
          className="w-full py-2 bg-red-600 hover:bg-red-700 rounded-lg"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
