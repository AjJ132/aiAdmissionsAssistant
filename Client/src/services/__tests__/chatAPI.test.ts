import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ChatAPIService, RateLimitError, APIUnavailableError } from '../chatAPI';

describe('ChatAPIService', () => {
  let chatService: ChatAPIService;
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    // Mock localStorage
    const storage: Record<string, string> = {};
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => storage[key] || null);
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation((key, value) => {
      storage[key] = value;
    });
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation((key) => {
      delete storage[key];
    });

    // Store original fetch
    originalFetch = global.fetch;

    // Create a new service instance for each test
    chatService = new ChatAPIService('https://test-api.example.com/chat');
  });

  afterEach(() => {
    vi.restoreAllMocks();
    global.fetch = originalFetch;
  });

  describe('APIUnavailableError', () => {
    it('should create an APIUnavailableError with default message', () => {
      const error = new APIUnavailableError();
      
      expect(error.name).toBe('APIUnavailableError');
      expect(error.message).toContain("I'm temporarily unavailable");
    });

    it('should create an APIUnavailableError with custom message', () => {
      const customMessage = 'Custom error message';
      const error = new APIUnavailableError(customMessage);
      
      expect(error.name).toBe('APIUnavailableError');
      expect(error.message).toBe(customMessage);
    });
  });

  describe('exponential backoff retry logic', () => {
    it('should retry on server error (5xx) up to 3 times', async () => {
      let attempts = 0;
      
      global.fetch = vi.fn().mockImplementation(() => {
        attempts++;
        if (attempts < 3) {
          return Promise.resolve({
            status: 500,
            ok: false,
          });
        }
        return Promise.resolve({
          status: 200,
          ok: true,
          json: () => Promise.resolve({
            response: 'Success after retries',
            thread_id: 'test-thread',
            status: 'completed',
          }),
        });
      });

      const result = await chatService.sendMessage('test message');
      
      expect(attempts).toBe(3);
      expect(result.response).toBe('Success after retries');
    });

    it('should throw APIUnavailableError after max retries exhausted', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 500,
        ok: false,
      });

      await expect(chatService.sendMessage('test message'))
        .rejects
        .toThrow(APIUnavailableError);
      
      // Should have been called 3 times (max retries)
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should throw APIUnavailableError on network failure after retries', async () => {
      global.fetch = vi.fn().mockRejectedValue(new TypeError('Network failure'));

      await expect(chatService.sendMessage('test message'))
        .rejects
        .toThrow(APIUnavailableError);
      
      // Should have been called 3 times (max retries)
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should not retry on rate limit errors (429)', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 429,
        ok: false,
        headers: new Headers({ 'Retry-After': '60' }),
        json: () => Promise.resolve({ message: 'Rate limited' }),
      });

      await expect(chatService.sendMessage('test message'))
        .rejects
        .toThrow(RateLimitError);
      
      // Should only be called once (no retries for rate limit)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry on 4xx errors (except 429)', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 400,
        ok: false,
      });

      await expect(chatService.sendMessage('test message'))
        .rejects
        .toThrow('HTTP error! status: 400');
      
      // Should only be called once (no retries for client errors)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should succeed on first try without retries', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: () => Promise.resolve({
          response: 'Success on first try',
          thread_id: 'test-thread',
          status: 'completed',
        }),
      });

      const result = await chatService.sendMessage('test message');
      
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(result.response).toBe('Success on first try');
    });
  });

  describe('thread_id handling', () => {
    it('should store thread_id from successful response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: () => Promise.resolve({
          response: 'Hello',
          thread_id: 'new-thread-id',
          status: 'completed',
        }),
      });

      await chatService.sendMessage('test');
      
      expect(chatService.getThreadId()).toBe('new-thread-id');
    });

    it('should include thread_id in subsequent requests', async () => {
      chatService.setThreadId('existing-thread');
      
      global.fetch = vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: () => Promise.resolve({
          response: 'Hello',
          thread_id: 'existing-thread',
          status: 'completed',
        }),
      });

      await chatService.sendMessage('test');
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('existing-thread'),
        })
      );
    });
  });

  describe('startNewConversation', () => {
    it('should clear thread_id', () => {
      chatService.setThreadId('some-thread');
      expect(chatService.getThreadId()).toBe('some-thread');
      
      chatService.startNewConversation();
      
      expect(chatService.getThreadId()).toBeNull();
    });
  });

  describe('hasActiveConversation', () => {
    it('should return true when thread_id exists', () => {
      chatService.setThreadId('test-thread');
      expect(chatService.hasActiveConversation()).toBe(true);
    });

    it('should return false when thread_id is null', () => {
      chatService.setThreadId(null);
      expect(chatService.hasActiveConversation()).toBe(false);
    });
  });
});
