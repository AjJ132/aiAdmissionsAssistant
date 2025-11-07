import React, { useState } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '@/hooks/useChat';
import { MessageCircle, X, RotateCcw } from 'lucide-react';

interface ChatFloatingModalProps {
  chatProvider: (children: (chat: ReturnType<typeof useChat>) => React.ReactNode) => React.ReactNode;
}

export const ChatFloatingModal: React.FC<ChatFloatingModalProps> = ({ 
  chatProvider,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 w-14 h-14 bg-[#FFB81C] hover:bg-[#E5A519] text-gray-900 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 z-[1000] flex items-center justify-center group"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
        </button>
      )}

      {/* Chat Modal */}
      {isOpen && chatProvider((chat) => (
        <div
          className="fixed bottom-6 right-6 w-[400px] h-[600px] bg-white rounded-lg shadow-2xl z-[1000] flex flex-col overflow-hidden border border-gray-200"
        >
          {/* Custom Header with Close Button */}
          <div className="flex-shrink-0 flex items-center justify-start px-4 py-3 bg-[#FFB81C] text-gray-900 gap-4">
              <MessageCircle className="w-5 h-5 flex-shrink-0" />
              <div className="font-semibold text-2xl">Chat Assistant</div>
            <button
              onClick={toggleChat}
              className="p-1 hover:bg-gray-700 hover:text-white rounded transition-colors flex-shrink-0 ml-auto"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Clear Chat Button - Subtle, in message area */}
          {chat.metadata.messageCount > 0 && (
            <div className="flex-shrink-0 px-4 py-2 bg-gray-50 border-b border-gray-200">
              <button
                onClick={chat.clearMessages}
                className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1.5 transition-colors"
                title="Clear conversation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Clear conversation</span>
              </button>
            </div>
          )}

          {/* Messages Area - with explicit flex-1 and min-height */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <MessageList
              messages={chat.messages}
              isLoading={chat.isLoading}
              isSearching={chat.messages.some(msg => msg.isSearching)}
            />
          </div>

          {/* Message Input - flex-shrink-0 to prevent compression */}
          <div className="flex-shrink-0">
            <MessageInput
              onSendMessage={chat.sendMessage}
              isLoading={chat.isLoading}
              canSendMessage={chat.canSendMessage}
            />
          </div>

          {/* Error Display */}
          {chat.error && (
            <div className="flex-shrink-0 p-4 bg-red-50 border-t border-red-200">
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
        </div>
      ))}
    </>
  );
};
