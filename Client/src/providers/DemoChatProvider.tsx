import React, { useCallback } from 'react';
import { useChat } from '@/hooks/useChat';
import { TestMessageService } from '@/services/TestMessageService';
import { ResponseService } from '@/services/ResponseService';

interface DemoChatProviderProps {
  children: (chat: ReturnType<typeof useChat> & { testMessage: () => void }) => React.ReactNode;
}

export const DemoChatProvider: React.FC<DemoChatProviderProps> = ({ children }) => {
  const chat = useChat('demo-chat');
  const testMessageService = TestMessageService.getInstance();
  const responseService = ResponseService.getInstance();

  const handleSendMessage = useCallback((text: string) => {
    if (!chat.canSendMessage || chat.isLoading) return;

    // Add user message
    chat.sendMessage(text);
    chat.setLoading(true);
    chat.setCanSendMessage(false);

    // For regular messages, just respond directly without search phase
    responseService.simulateTypingDelay(() => {
      const mockResponse = responseService.getRandomResponse();
      const responseId = chat.addMessage({
        text: mockResponse.text,
        isUser: false,
        sources: mockResponse.sources,
      });

      // Simulate streaming effect
      chat.updateMessage(responseId, { isStreaming: true });
      
      responseService.simulateTypingDelay(() => {
        chat.updateMessage(responseId, { isStreaming: false });
        chat.setLoading(false);
        chat.setCanSendMessage(true);
      }, 1000);
    }, 1000);
  }, [chat, responseService]);

  const handleTestMessage = useCallback(() => {
    if (!chat.canSendMessage || chat.isLoading) return;

    const { userMessage, response, sources } = testMessageService.getTestMessage();
    
    // Add user message
    chat.sendMessage(userMessage.text);
    chat.setLoading(true);
    chat.setCanSendMessage(false);

    // Simulate search delay
    responseService.simulateTypingDelay(() => {
      const searchMessageId = chat.addMessage({
        text: responseService.getSearchingMessage(),
        isUser: false,
        isSearching: true,
      });

      // After 3 seconds, update with full response
      responseService.simulateSearchDelay(() => {
        chat.updateMessage(searchMessageId, {
          text: response,
          isSearching: false,
          sources: sources
        });
        chat.setLoading(false);
        chat.setCanSendMessage(true);
      }, 3000);
    }, 1000);
  }, [chat, testMessageService, responseService]);

  const chatWithDemo = {
    ...chat,
    sendMessage: handleSendMessage,
    testMessage: handleTestMessage,
  };

  return <>{children(chatWithDemo)}</>;
};
