import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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

  const handleSendMessage = () => {
    if (inputValue.trim() && canSendMessage && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="px-4 pb-4 pt-2 bg-white border-t border-gray-100">
      <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 py-2 focus-within:border-gray-300 transition-colors">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={!canSendMessage || isLoading}
          className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-sm px-0"
        />
        <Button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !canSendMessage || isLoading}
          size="sm"
          className="rounded-full h-8 w-8 p-0 flex items-center justify-center"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
