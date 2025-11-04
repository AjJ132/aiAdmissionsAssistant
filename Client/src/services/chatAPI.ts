/**
 * Service for managing chat API communication with stateless architecture.
 * 
 * This service implements the client side of the stateless chat architecture:
 * - Stores thread_id in localStorage for conversation continuity
 * - Sends thread_id with each request
 * - Handles new conversations by clearing thread_id
 * - Implements client-side rate limiting
 */

const THREAD_ID_STORAGE_KEY = 'chat_thread_id';
const RATE_LIMIT_STORAGE_KEY = 'chat_rate_limit';

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

export interface RateLimitInfo {
  requestCount: number;
  windowStart: number;
  retryAfter?: number;
}

export class RateLimitError extends Error {
  retryAfter: number;
  
  constructor(message: string, retryAfter: number) {
    super(message);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}

export class ChatAPIService {
  private apiEndpoint: string;
  private threadId: string | null;
  private maxRequestsPerMinute: number = 15; // Client-side limit (slightly lower than server)
  private rateLimitWindowMs: number = 60000; // 1 minute

  constructor(apiEndpoint: string = '/api/chat') {
    this.apiEndpoint = apiEndpoint;
    // Load thread_id from localStorage if exists
    this.threadId = localStorage.getItem(THREAD_ID_STORAGE_KEY);
  }

  /**
   * Check if the request is allowed based on client-side rate limiting
   */
  private checkRateLimit(): void {
    const now = Date.now();
    const rateLimitData = localStorage.getItem(RATE_LIMIT_STORAGE_KEY);
    
    let rateLimitInfo: RateLimitInfo = {
      requestCount: 0,
      windowStart: now
    };
    
    if (rateLimitData) {
      try {
        rateLimitInfo = JSON.parse(rateLimitData);
      } catch {
        // Invalid data, start fresh
        rateLimitInfo = { requestCount: 0, windowStart: now };
      }
    }
    
    // Check if we're in a new time window
    const windowElapsed = now - rateLimitInfo.windowStart;
    if (windowElapsed >= this.rateLimitWindowMs) {
      // Start a new window
      rateLimitInfo = {
        requestCount: 1,
        windowStart: now
      };
    } else {
      // Check if we've exceeded the limit
      if (rateLimitInfo.requestCount >= this.maxRequestsPerMinute) {
        const timeRemaining = Math.ceil((this.rateLimitWindowMs - windowElapsed) / 1000);
        throw new RateLimitError(
          `Rate limit exceeded. Please wait ${timeRemaining} seconds before sending another message.`,
          timeRemaining
        );
      }
      
      // Increment the counter
      rateLimitInfo.requestCount++;
    }
    
    // Save updated rate limit info
    localStorage.setItem(RATE_LIMIT_STORAGE_KEY, JSON.stringify(rateLimitInfo));
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
   * @throws RateLimitError if rate limit is exceeded
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    // Check client-side rate limit first
    this.checkRateLimit();
    
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

      // Handle rate limit response from server
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
        const data = await response.json();
        throw new RateLimitError(
          data.message || 'Rate limit exceeded. Please try again later.',
          retryAfter
        );
      }

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
      if (error instanceof RateLimitError) {
        throw error;
      }
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
  import.meta.env.VITE_API_URL
);
