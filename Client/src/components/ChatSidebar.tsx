import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { MessageList } from '@/components/chat/MessageList';
import { MessageInput } from '@/components/chat/MessageInput';
import type { Message } from '@/hooks/useChat';

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onWidthChange?: (width: number) => void;
  chatProvider: {
    sendMessage: (text: string) => void;
    testMessage?: () => void;
    messages: Message[];
    isLoading: boolean;
    canSendMessage: boolean;
    clearMessages: () => void;
  };
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ 
  isOpen, 
  onToggle, 
  onWidthChange, 
  chatProvider
}) => {
  const {
    messages,
    isLoading,
    canSendMessage,
  } = chatProvider;

  const [chatWidth, setChatWidth] = useState(500);
  const [isResizing, setIsResizing] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  
  const MIN_WIDTH = 350;
  const MAX_WIDTH = 800;

  // Handle message sending - delegate to chat provider
  const handleSendMessage = (messageText: string) => {
    // Type 'test' to trigger test message if available
    if (messageText.toLowerCase().trim() === 'test' && chatProvider?.testMessage) {
      chatProvider.testMessage();
      return;
    }

    if (chatProvider?.sendMessage) {
      chatProvider.sendMessage(messageText);
    }
  };

  // Handle resize functionality
  useEffect(() => {
    let animationFrameId: number;
    
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      
      animationFrameId = requestAnimationFrame(() => {
        const newWidth = window.innerWidth - e.clientX;
        const clampedWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth));
        
        setChatWidth(clampedWidth);
        onWidthChange?.(clampedWidth);
      });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove, { passive: true });
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      document.body.style.pointerEvents = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      document.body.style.pointerEvents = '';
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [isResizing, onWidthChange]);

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <Button
        size="icon"
        className={`fixed bottom-5 w-15 h-15 rounded-full text-2xl z-[1001] shadow-lg transition-all duration-500 ease-in-out transform hover:scale-110 active:scale-95 ${
          isOpen 
            ? 'bg-foreground hover:bg-secondary text-primary hover:text-foreground' 
            : 'bg-primary hover:bg-secondary text-primary-foreground hover:text-foreground chat-button-bounce'
        }`}
        onClick={onToggle}
        style={{
          right: isOpen ? `${chatWidth + 20}px` : '20px'
        }}
      >
        <span className={`transition-all duration-500 ${isOpen ? 'rotate-180 scale-110' : 'rotate-0 scale-100'}`}>
          {isOpen ? '×' : '💬'}
        </span>
      </Button>

      {/* Chat Sidebar */}
      <div
        ref={chatRef}
        className={`fixed top-0 h-screen bg-background border-l border-border z-[1000] flex flex-col overflow-hidden ${
          isOpen ? 'right-0 shadow-[-4px_0_12px_rgba(0,0,0,0.1)]' : '-right-[500px]'
        } ${!isResizing ? 'transition-all duration-300 ease-in-out' : ''}`}
        style={{
          width: `${chatWidth}px`,
          right: isOpen ? '0' : `-${chatWidth}px`
        }}
      >
        {/* Resize Handle */}
        <div
          className="absolute left-0 top-0 w-2 h-full bg-transparent hover:bg-primary/20 cursor-col-resize transition-colors duration-200 z-[1002] group"
          onMouseDown={handleResizeStart}
        >
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-1 h-12 bg-secondary rounded-full opacity-70 group-hover:opacity-100 transition-opacity duration-200 shadow-sm"></div>
          </div>
          <div className="absolute left-0.5 top-1/2 transform -translate-y-1/2 w-0.5 h-8 bg-border rounded-full opacity-40 group-hover:opacity-60 transition-opacity duration-200"></div>
          <div className="absolute left-0.5 top-1/2 transform translate-y-2 w-0.5 h-6 bg-border rounded-full opacity-40 group-hover:opacity-60 transition-opacity duration-200"></div>
          <div className="absolute left-0.5 top-1/2 transform -translate-y-2 w-0.5 h-6 bg-border rounded-full opacity-40 group-hover:opacity-60 transition-opacity duration-200"></div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 min-h-0 flex flex-col bg-background">
          {/* Header with New Chat button */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="text-lg font-semibold">Graduate Admissions Assistant</h2>
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => chatProvider?.clearMessages()}
                className="text-xs"
              >
                + New Chat
              </Button>
            )}
          </div>
          
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isSearching={messages.some(msg => msg.isSearching)}
          />
        </div>

        {/* Input Area */}
        <MessageInput
          onSendMessage={handleSendMessage}
          onTestMessage={chatProvider?.testMessage}
          isLoading={isLoading}
          canSendMessage={canSendMessage}
          placeholder={
            isLoading 
              ? "KSU Graduate Admissions Assistant is typing..." 
              : !canSendMessage 
                ? "Please wait for response..." 
                : "Ask about graduate admissions..."
          }
        />
      </div>
    </>
  );
};