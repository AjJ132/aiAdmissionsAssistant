import React, { useRef, useEffect } from 'react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '@/hooks/useChat';
import { TypingIndicator } from './TypingIndicator';
import { WelcomeMessage } from './WelcomeMessage';
import { ReportIssueButton} from './ReportIssueButton';
import type { ReportData } from './ReportIssueButton';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  isSearching?: boolean;
  onReportIssue?: (data: ReportData) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  isSearching = false,
  onReportIssue,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle report issue
  const handleReport = (data: ReportData) => {
    console.log('Issue reported:', data);
    
    // Store in localStorage for demo (in production, send to API)
    try {
      const existingReports = JSON.parse(localStorage.getItem('chatbot_reports') || '[]');
      existingReports.push(data);
      localStorage.setItem('chatbot_reports', JSON.stringify(existingReports));
      
      // Call parent callback if provided
      onReportIssue?.(data);
    } catch (error) {
      console.error('Error saving report:', error);
    }
  };

  // Function to get the user's question for a bot response
  const getUserQuestionForMessage = (messageIndex: number): string => {
    // Look for the previous user message
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].isUser) {
        return messages[i].text;
      }
    }
    return 'Question not found';
  };

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 h-full overflow-auto">
        <WelcomeMessage />
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 h-full">
      <div className="px-4 py-6 space-y-6">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start gap-3 max-w-[85%] ${message.isUser ? 'flex-row-reverse' : ''}`}>
              {!message.isUser && (
                <Avatar className="h-7 w-7 bg-blue-50 flex-shrink-0 border-0">
                  <AvatarFallback className="text-blue-600 text-xs font-medium">
                    AI
                  </AvatarFallback>
                </Avatar>
              )}
              {message.isUser && (
                <Avatar className="h-7 w-7 bg-gray-100 flex-shrink-0 border-0">
                  <AvatarFallback className="text-gray-600 text-xs font-medium">
                    U
                  </AvatarFallback>
                </Avatar>
              )}
              <div className="flex flex-col gap-1">
                <div className={`${message.isUser ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'} rounded-2xl px-4 py-2.5`}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => (
                        <h1 className={`text-base font-bold mt-3 mb-2 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className={`text-sm font-bold mt-3 mb-1.5 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className={`text-sm font-semibold mt-2 mb-1 ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                          {children}
                        </h3>
                      ),
                      h4: ({ children }) => (
                        <h4 className={`text-sm font-medium mt-2 mb-1 ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                          {children}
                        </h4>
                      ),
                      h5: ({ children }) => (
                        <h5 className={`text-xs font-medium mt-1.5 mb-0.5 ${message.isUser ? 'text-white' : 'text-gray-800'}`}>
                          {children}
                        </h5>
                      ),
                      h6: ({ children }) => (
                        <h6 className={`text-xs font-normal mt-1.5 mb-0.5 ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                          {children}
                        </h6>
                      ),
                      p: ({ children }) => (
                        <p className={`text-sm leading-relaxed ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                          {children}
                        </p>
                      ),
                      strong: ({ children }) => (
                        <strong className={`font-semibold ${message.isUser ? 'text-white' : 'text-gray-900'}`}>
                          {children}
                        </strong>
                      ),
                      ul: ({ children }) => (
                        <ul className={`text-sm my-2 space-y-1 ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className={`text-sm my-2 space-y-1 ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className={`text-sm ${message.isUser ? 'text-white' : 'text-gray-700'}`}>
                          {children}
                        </li>
                      ),
                    }}
                  >
                    {message.text}
                  </ReactMarkdown>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200/20">
                      <p className="text-xs text-gray-400 mb-1.5">Sources:</p>
                      <div className="space-y-1">
                        {message.sources
                          .filter(source => {
                            // Only show sources that are valid URLs (not file IDs) THis is a backup
                            try {
                              const url = new URL(source);
                              return url.protocol === 'http:' || url.protocol === 'https:';
                            } catch {
                              return false;
                            }
                          })
                          .map((source, index) => (
                            <div key={index} className="text-xs text-blue-500 hover:text-blue-700">
                              <a href={source} target="_blank" rel="noopener noreferrer">
                                {source}
                              </a>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Report Issue Button - Only for bot responses */}
                {!message.isUser && !isSearching && (
                  <div className="ml-2">
                    <ReportIssueButton
                      messageId={message.id}
                      question={getUserQuestionForMessage(index)}
                      response={message.text}
                      onReport={handleReport}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {(isLoading || isSearching) && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
};