import React, { useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '@/hooks/useChat';
import { TypingIndicator } from './TypingIndicator';
import { WelcomeMessage } from './WelcomeMessage';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  isSearching?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  isSearching = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <ScrollArea className="flex-1 h-full">
        <div className="p-4">
          <WelcomeMessage />
        </div>
      </ScrollArea>
    );
  }

  return (
    <ScrollArea className="flex-1 h-full">
      <div className="p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-3 max-w-[80%] ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {!message.isUser && (
                <Avatar className="h-8 w-8 bg-blue-100 flex-shrink-0 border">
                  <AvatarFallback className="text-blue-600 text-sm font-medium">
                    AI
                  </AvatarFallback>
                </Avatar>
              )}
              {message.isUser && (
                <Avatar className="h-8 w-8 bg-gray-100 flex-shrink-0 border">
                  <AvatarFallback className="text-gray-600 text-sm font-medium">
                    U
                  </AvatarFallback>
                </Avatar>
              )}
              <Card className={`${message.isUser ? 'bg-blue-600 text-white' : 'bg-gray-50 border-gray-200'} py-2`}>
                <CardContent className="py-0 px-3 content-center items-center">
                  {/* <div className="prose prose-sm max-w-none"> */}
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h1: ({ children }) => (
                          <h1 className={`!text-lg font-bold !mt-4 mb-1 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 className={`!text-base font-bold mt-4 mb-1 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 className={`text-sm font-semibold mt-1 mb-1 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                            {children}
                          </h3>
                        ),
                        h4: ({ children }) => (
                          <h4 className={`!text-sm font-medium mt-1 mb-1 ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </h4>
                        ),
                        h5: ({ children }) => (
                          <h5 className={`!text-xs font-medium mt-1 mb-1 ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </h5>
                        ),
                        h6: ({ children }) => (
                          <h6 className={`!text-xs font-normal mt-1 mb-1 ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                            {children}
                          </h6>
                        ),
                        p: ({ children }) => (
                          <p className={`!mt-0 text-sm ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </p>
                        ),
                        strong: ({ children }) => (
                          <strong className={`font-semibold ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                            {children}
                          </strong>
                        ),
                        ul: ({ children }) => (
                          <ul className={`text-sm ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol className={`text-sm ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => (
                          <li className={`text-sm ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                            {children}
                          </li>
                        ),
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  {/* </div> */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-500 mb-1">Sources:</p>
                      <div className="space-y-1">
                        {message.sources.map((source, index) => (
                          <div key={index} className="text-xs text-blue-600 hover:text-blue-800">
                            <a href={source} target="_blank" rel="noopener noreferrer">
                              {source}
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        ))}
        
        {(isLoading || isSearching) && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
};
