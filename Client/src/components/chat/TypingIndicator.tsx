import React from 'react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="px-4 py-2">
      <div className="flex items-start gap-3">
        <Avatar className="h-7 w-7 bg-blue-50 flex-shrink-0 border-0">
          <AvatarFallback className="text-blue-600 text-xs font-medium">
            KSU
          </AvatarFallback>
        </Avatar>
        <div className="flex items-center bg-white border border-gray-200 rounded-2xl px-4 py-3">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};
