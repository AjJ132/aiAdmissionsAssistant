import { useState, useCallback, useRef } from 'react';

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  isTyping?: boolean;
  isStreaming?: boolean;
  isSearching?: boolean;
  sources?: string[];
  timestamp: Date;
}

export interface ChatMetadata {
  id: string;
  title?: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  isActive: boolean;
}

export interface ChatState {
  messages: Message[];
  metadata: ChatMetadata;
  isLoading: boolean;
  canSendMessage: boolean;
  error: string | null;
}

export interface ChatActions {
  sendMessage: (text: string) => void;
  clearMessages: () => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  setCanSendMessage: (canSend: boolean) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => string;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  deleteMessage: (id: string) => void;
}

export interface UseChatReturn extends ChatState, ChatActions {}

export const useChat = (initialChatId?: string): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [canSendMessage, setCanSendMessage] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const messageIdCounter = useRef(0);
  
  const generateMessageId = useCallback(() => {
    return `msg_${Date.now()}_${++messageIdCounter.current}`;
  }, []);

  const generateChatId = useCallback(() => {
    return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  const [metadata, setMetadata] = useState<ChatMetadata>(() => ({
    id: initialChatId || generateChatId(),
    createdAt: new Date(),
    updatedAt: new Date(),
    messageCount: 0,
    isActive: true,
  }));

  const addMessage = useCallback((messageData: Omit<Message, 'id' | 'timestamp'>): string => {
    const id = generateMessageId();
    const message: Message = {
      ...messageData,
      id,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, message]);
    setMetadata(prev => ({
      ...prev,
      updatedAt: new Date(),
      messageCount: prev.messageCount + 1,
    }));
    
    return id;
  }, [generateMessageId]);

  const updateMessage = useCallback((id: string, updates: Partial<Message>) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === id ? { ...msg, ...updates } : msg
      )
    );
  }, []);

  const deleteMessage = useCallback((id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
    setMetadata(prev => ({
      ...prev,
      updatedAt: new Date(),
      messageCount: Math.max(0, prev.messageCount - 1),
    }));
  }, []);

  const sendMessage = useCallback((text: string) => {
    if (!text.trim() || !canSendMessage || isLoading) return;
    
    addMessage({
      text: text.trim(),
      isUser: true,
    });
  }, [addMessage, canSendMessage, isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setMetadata(prev => ({
      ...prev,
      updatedAt: new Date(),
      messageCount: 0,
    }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  return {
    // State
    messages,
    metadata,
    isLoading,
    canSendMessage,
    error,
    
    // Actions
    sendMessage,
    clearMessages,
    setError,
    setLoading,
    setCanSendMessage,
    addMessage,
    updateMessage,
    deleteMessage,
  };
};
