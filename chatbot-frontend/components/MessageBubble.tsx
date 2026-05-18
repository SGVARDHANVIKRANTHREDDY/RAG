'use client';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

interface Message {
  id: number;
  role: string;
  content: string;
  sources?: any[];
}

export default function MessageBubble({ 
  message, 
  isStreaming = false 
}: { 
  message: Message; 
  isStreaming?: boolean;
}) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex $\{isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-lg p-4 $\{
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
        }`}
      >
        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
          {message.content}
        </ReactMarkdown>
        
        {isStreaming && (
          <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
        )}
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <p className="text-sm font-semibold mb-2">Sources:</p>
            {message.sources.map((source, idx) => (
              <div key={idx} className="text-xs mb-1">
                📄 {source.filename} (chunk {source.chunk})
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
