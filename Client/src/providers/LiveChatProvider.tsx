import React, { useCallback, useRef, useEffect, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { chatAPIService, ChatAPIService, APIUnavailableError } from '@/services/chatAPI';

// Fallback message constant
const FALLBACK_MESSAGE = "I'm temporarily unavailable. Please try again in a few moments or contact the Graduate Admissions office directly at graduate@kennesaw.edu or 470-578-4377.";

interface LiveChatProviderProps {
  children: (chat: ReturnType<typeof useChat> & { showContactUs: boolean; setShowContactUs: (show: boolean) => void }) => React.ReactNode;
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
  const [showContactUs, setShowContactUs] = useState(false);

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
    setShowContactUs(false);

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
      
      // Check if it's an API unavailability error (after retries exhausted)
      if (error instanceof APIUnavailableError) {
        // Show fallback message and Contact Us button
        chat.addMessage({
          text: FALLBACK_MESSAGE,
          isUser: false,
          isSearching: false,
          isStreaming: false,
        });
        setShowContactUs(true);
        chat.setError(null); // Don't show error banner, the fallback message is sufficient
      } else {
        // Add generic error message for other errors
        chat.addMessage({
          text: 'Failed to send message. Please try again.',
          isUser: false,
          isSearching: false,
          isStreaming: false,
        });
        chat.setError('Failed to send message. Please try again.');
      }
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
    setShowContactUs(false);
    console.log('Started new conversation');
  }, [chat]);

  const chatWithLive = {
    ...chat,
    sendMessage,
    clearMessages,
    showContactUs,
    setShowContactUs,
  };

  return <>{children(chatWithLive)}</>;
};
