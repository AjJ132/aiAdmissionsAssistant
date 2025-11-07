import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Send } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  canSendMessage: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isLoading,
  canSendMessage,
  placeholder = "Message KSU Chatbot...",
}) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSendMessage = () => {
    if (inputValue.trim() && canSendMessage && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  return (
    <div className="px-4 pb-4 pt-2 bg-white border-t border-gray-200">
      <div className="flex items-center gap-2 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-[#FFB81C] focus-within:ring-1 focus-within:ring-[#FFB81C] transition-all">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={!canSendMessage || isLoading}
          rows={1}
          className="flex-1 bg-transparent border-0 focus:outline-none focus:ring-0 text-sm resize-none max-h-[120px] placeholder:text-gray-400 leading-5 py-0 m-0"
          style={{ minHeight: '20px' }}
        />
        <Button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !canSendMessage || isLoading}
          size="sm"
          className="rounded-full h-8 w-8 p-0 flex items-center justify-center flex-shrink-0 bg-[#FFB81C] hover:bg-[#E5A519] text-gray-900"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
