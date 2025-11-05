import React, { useCallback, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { chatAPIService, ChatAPIService } from '@/services/chatAPI';

interface LiveChatProviderProps {
  children: (chat: ReturnType<typeof useChat>) => React.ReactNode;
  apiEndpoint?: string;
  chatId?: string;
}

export const LiveChatProvider: React.FC<LiveChatProviderProps> = ({ 
  children, 
  apiEndpoint,
  chatId 
}) => {
  const chat = useChat(chatId);
  const currentMessageIdRef = useRef<string | null>(null);
  const apiServiceRef = useRef<ChatAPIService>(
    apiEndpoint ? new ChatAPIService(apiEndpoint) : chatAPIService
  );

  // Load thread_id on mount
  useEffect(() => {
    const threadId = apiServiceRef.current.getThreadId();
    if (threadId) {
      console.log('Loaded existing thread_id:', threadId);
    }
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!chat.canSendMessage || chat.isLoading) return;

    // Add user message
    chat.sendMessage(text);
    chat.setLoading(true);
    chat.setCanSendMessage(false);
    chat.setError(null);

    try {
      // Call the stateless chat API
      const response = await apiServiceRef.current.sendMessage(text);

      if (response.status === 'completed') {
        // Add the AI response message
        chat.addMessage({
          text: response.response,
          isUser: false,
          isSearching: false,
          isStreaming: false,
          sources: response.sources,
        });

        console.log('Conversation thread_id:', response.thread_id);
      } else {
        // Handle error response
        chat.addMessage({
          text: response.error || 'Failed to get response',
          isUser: false,
          isSearching: false,
          isStreaming: false,
        });
        chat.setError(response.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      chat.addMessage({
        text: 'Failed to send message. Please try again.',
        isUser: false,
        isSearching: false,
        isStreaming: false,
      });
      chat.setError('Failed to send message. Please try again.');
    } finally {
      chat.setLoading(false);
      chat.setCanSendMessage(true);
      currentMessageIdRef.current = null;
    }
  }, [chat]);

  const clearMessages = useCallback(() => {
    // Clear messages and start new conversation
    chat.clearMessages();
    apiServiceRef.current.startNewConversation();
    console.log('Started new conversation');
  }, [chat]);

  const chatWithLive = {
    ...chat,
    sendMessage,
    clearMessages,
  };

  return <>{children(chatWithLive)}</>;
};
