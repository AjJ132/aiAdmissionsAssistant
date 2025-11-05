import React, { useRef, useState } from 'react';
import { ChatHeader } from './ChatHeader';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '@/hooks/useChat';

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onWidthChange?: (width: number) => void;
  chatProvider: (children: (chat: ReturnType<typeof useChat>) => React.ReactNode) => React.ReactNode;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ 
  isOpen, 
  onToggle, 
  onWidthChange,
  chatProvider,
}) => {
  const [chatWidth, setChatWidth] = useState(500);
  const [isResizing, setIsResizing] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  
  const MIN_WIDTH = 350;
  const MAX_WIDTH = 800;

  // Handle resize functionality
  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    
    const startX = e.clientX;
    const startWidth = chatWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startWidth - (e.clientX - startX)));
      setChatWidth(newWidth);
      onWidthChange?.(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div
      ref={chatRef}
      className="fixed top-0 h-screen bg-gray-50 border-l border-gray-200 z-[1000] flex flex-col overflow-hidden shadow-xl"
      style={{
        width: `${chatWidth}px`,
        right: isOpen ? '0' : `-${chatWidth}px`,
        maxHeight: '100vh',
        transition: isResizing ? 'none' : 'right 0.3s ease-in-out'
      }}
    >
      {/* Resize Handle */}
      <div
        className="absolute left-0 top-0 w-1.5 h-full bg-transparent hover:bg-blue-100 cursor-col-resize transition-colors duration-150 z-[1002] group"
        onMouseDown={handleResizeStart}
      >
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-0.5 h-10 bg-gray-300 rounded-full opacity-0 group-hover:opacity-60 transition-opacity duration-150"></div>
        </div>
      </div>

      {chatProvider((chat) => (
        <>
          {/* Chat Header */}
          <ChatHeader
            onToggle={onToggle}
            onClear={chat.clearMessages}
            messageCount={chat.metadata.messageCount}
          />

          {/* Messages Area */}
          <MessageList
            messages={chat.messages}
            isLoading={chat.isLoading}
            isSearching={chat.messages.some(msg => msg.isSearching)}
          />

          {/* Message Input */}
          <MessageInput
            onSendMessage={chat.sendMessage}
            isLoading={chat.isLoading}
            canSendMessage={chat.canSendMessage}
          />

          {/* Error Display */}
          {chat.error && (
            <div className="p-4 bg-red-50 border-t border-red-200">
              <div className="text-sm text-red-600">
                <strong>Error:</strong> {chat.error}
              </div>
              <button
                onClick={() => chat.setError(null)}
                className="text-xs text-red-500 hover:text-red-700 mt-1"
              >
                Dismiss
              </button>
            </div>
          )}
        </>
      ))}
    </div>
  );
};
