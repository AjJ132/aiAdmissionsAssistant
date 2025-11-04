/**
 * Service for managing chat API communication with stateless architecture.
 * 
 * This service implements the client side of the stateless chat architecture:
 * - Stores thread_id in localStorage for conversation continuity
 * - Sends thread_id with each request
 * - Handles new conversations by clearing thread_id
 */

const THREAD_ID_STORAGE_KEY = 'chat_thread_id';

export interface ChatMessage {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
  status: string;
  sources?: string[];
  error?: string;
}

export class ChatAPIService {
  private apiEndpoint: string;
  private threadId: string | null;

  constructor(apiEndpoint: string = '/api/chat') {
    this.apiEndpoint = apiEndpoint;
    // Load thread_id from localStorage if exists
    this.threadId = localStorage.getItem(THREAD_ID_STORAGE_KEY);
  }

  /**
   * Get the current thread ID
   */
  getThreadId(): string | null {
    return this.threadId;
  }

  /**
   * Set the thread ID manually (useful for loading existing conversations)
   */
  setThreadId(threadId: string | null): void {
    this.threadId = threadId;
    if (threadId) {
      localStorage.setItem(THREAD_ID_STORAGE_KEY, threadId);
    } else {
      localStorage.removeItem(THREAD_ID_STORAGE_KEY);
    }
  }

  /**
   * Send a message to the chat API
   * 
   * @param message - The user's message
   * @returns Promise with the chat response
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const requestBody: ChatMessage = {
        message: message,
      };

      // Include thread_id if we have one (continuing conversation)
      if (this.threadId) {
        requestBody.thread_id = this.threadId;
      }

      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Store thread_id for future requests
      if (data.thread_id) {
        this.threadId = data.thread_id;
        localStorage.setItem(THREAD_ID_STORAGE_KEY, data.thread_id);
      }

      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Start a new conversation by clearing the thread_id
   */
  startNewConversation(): void {
    this.threadId = null;
    localStorage.removeItem(THREAD_ID_STORAGE_KEY);
  }

  /**
   * Check if there's an active conversation (has thread_id)
   */
  hasActiveConversation(): boolean {
    return this.threadId !== null;
  }
}

// Export a singleton instance for convenience
export const chatAPIService = new ChatAPIService(
  import.meta.env.VITE_API_ENDPOINT || '/api/chat'
);
