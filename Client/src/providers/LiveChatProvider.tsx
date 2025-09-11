import React, { useCallback, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';

interface LiveChatProviderProps {
  children: (chat: ReturnType<typeof useChat> & { testMessage: () => void }) => React.ReactNode;
  apiEndpoint?: string;
  chatId?: string;
}

interface SSEMessage {
  type: 'message' | 'searching' | 'sources' | 'error' | 'done';
  content?: string;
  sources?: string[];
  error?: string;
}

export const LiveChatProvider: React.FC<LiveChatProviderProps> = ({ 
  children, 
  apiEndpoint = '/api/chat',
  chatId 
}) => {
  const chat = useChat(chatId);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentMessageIdRef = useRef<string | null>(null);

  // Cleanup SSE connection on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSSEMessage = useCallback((event: MessageEvent) => {
    try {
      const data: SSEMessage = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          if (data.content) {
            if (currentMessageIdRef.current) {
              // Update existing message
              chat.updateMessage(currentMessageIdRef.current, {
                text: data.content,
                isStreaming: true,
              });
            } else {
              // Create new message
              const messageId = chat.addMessage({
                text: data.content,
                isUser: false,
                isStreaming: true,
              });
              currentMessageIdRef.current = messageId;
            }
          }
          break;
          
        case 'searching':
          if (data.content) {
            const searchMessageId = chat.addMessage({
              text: data.content,
              isUser: false,
              isSearching: true,
            });
            currentMessageIdRef.current = searchMessageId;
          }
          break;
          
        case 'sources':
          if (data.sources && currentMessageIdRef.current) {
            chat.updateMessage(currentMessageIdRef.current, {
              sources: data.sources,
            });
          }
          break;
          
        case 'error':
          chat.setError(data.error || 'An error occurred');
          chat.setLoading(false);
          chat.setCanSendMessage(true);
          break;
          
        case 'done':
          if (currentMessageIdRef.current) {
            chat.updateMessage(currentMessageIdRef.current, {
              isStreaming: false,
              isSearching: false,
            });
          }
          chat.setLoading(false);
          chat.setCanSendMessage(true);
          currentMessageIdRef.current = null;
          break;
      }
    } catch (error) {
      console.error('Error parsing SSE message:', error);
      chat.setError('Failed to parse server response');
      chat.setLoading(false);
      chat.setCanSendMessage(true);
    }
  }, [chat]);

  const handleSSEError = useCallback(() => {
    chat.setError('Connection lost. Please try again.');
    chat.setLoading(false);
    chat.setCanSendMessage(true);
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, [chat]);

  const sendMessage = useCallback(async (text: string) => {
    if (!chat.canSendMessage || chat.isLoading) return;

    // Add user message
    chat.sendMessage(text);
    chat.setLoading(true);
    chat.setCanSendMessage(false);
    chat.setError(null);
    currentMessageIdRef.current = null;

    try {
      // Close existing connection if any
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create new SSE connection
      const url = new URL(apiEndpoint, window.location.origin);
      url.searchParams.set('message', text);
      url.searchParams.set('chatId', chat.metadata.id);
      
      eventSourceRef.current = new EventSource(url.toString());
      
      eventSourceRef.current.onmessage = handleSSEMessage;
      eventSourceRef.current.onerror = handleSSEError;
      
    } catch (error) {
      console.error('Error sending message:', error);
      chat.setError('Failed to send message. Please try again.');
      chat.setLoading(false);
      chat.setCanSendMessage(true);
    }
  }, [chat, apiEndpoint, handleSSEMessage, handleSSEError]);

  const handleTestMessage = useCallback(() => {
    const testMessage = "What are the admission requirements for the Computer Science graduate program?";
    sendMessage(testMessage);
  }, [sendMessage]);

  const chatWithLive = {
    ...chat,
    sendMessage,
    testMessage: handleTestMessage,
  };

  return <>{children(chatWithLive)}</>;
};
