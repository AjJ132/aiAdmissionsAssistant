import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface ChatHeaderProps {
  onToggle: () => void;
  onClear: () => void;
  messageCount: number;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  onClear,
  messageCount,
}) => {
  return (
    <div className="px-4 py-3 border-b border-gray-100 bg-white">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-gray-700">
          KSU Chatbot
        </h2>
        {messageCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-50 h-8 px-3 ml-auto"
          >
            <Plus className="h-3.5 w-3.5 mr-1.5" />
            New Chat
          </Button>
        )}
      </div>
    </div>
  );
};
