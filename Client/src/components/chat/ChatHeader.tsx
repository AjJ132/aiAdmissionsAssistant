import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { X, MessageSquare } from 'lucide-react';

interface ChatHeaderProps {
  onToggle: () => void;
  onClear: () => void;
  messageCount: number;
  isDemoMode?: boolean;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  onToggle,
  onClear,
  messageCount,
}) => {
  return (
    <Card className="rounded-none border-b py-0">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-800">
                AI Assistant
              </h2>
            </div>
            {messageCount > 0 && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                {messageCount} message{messageCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {messageCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClear}
                className="text-gray-500 hover:text-gray-700"
              >
                Clear
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
