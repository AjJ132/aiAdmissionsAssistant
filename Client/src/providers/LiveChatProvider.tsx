import React, { useCallback, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { chatAPIService, ChatAPIService } from '@/services/chatAPI';

interface LiveChatProviderProps {
  children: (chat: ReturnType<typeof useChat> & { testMessage: () => void }) => React.ReactNode;
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

    // Add "thinking" message
    const thinkingMessageId = chat.addMessage({
      text: 'Thinking...',
      isUser: false,
      isSearching: true,
    });
    currentMessageIdRef.current = thinkingMessageId;

    try {
      // Call the stateless chat API
      const response = await apiServiceRef.current.sendMessage(text);

      if (response.status === 'completed') {
        // Update the thinking message with the actual response
        chat.updateMessage(thinkingMessageId, {
          text: response.response,
          isSearching: false,
          isStreaming: false,
          sources: response.sources,
        });

        console.log('Conversation thread_id:', response.thread_id);
      } else {
        // Handle error response
        chat.updateMessage(thinkingMessageId, {
          text: response.error || 'Failed to get response',
          isSearching: false,
          isStreaming: false,
        });
        chat.setError(response.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Update thinking message to show error
      chat.updateMessage(thinkingMessageId, {
        text: 'Failed to send message. Please try again.',
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

  const handleTestMessage = useCallback(() => {
    const testMessage = "What are the admission requirements for the Computer Science graduate program?";
    sendMessage(testMessage);
  }, [sendMessage]);

  const clearMessages = useCallback(() => {
    // Clear messages and start new conversation
    chat.clearMessages();
    apiServiceRef.current.startNewConversation();
    console.log('Started new conversation');
  }, [chat]);

  const chatWithLive = {
    ...chat,
    sendMessage,
    testMessage: handleTestMessage,
    clearMessages,
  };

  return <>{children(chatWithLive)}</>;
};
