import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export const TypingIndicator: React.FC = () => {
  return (
    <Card className="mb-4 bg-gray-50 border-gray-200">
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          <Avatar className="h-8 w-8 bg-blue-100">
            <AvatarFallback className="text-blue-600 text-sm font-medium">
              AI
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <div className="flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-sm text-gray-500 ml-2">AI is typing...</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
