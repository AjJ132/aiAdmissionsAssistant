import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useChat } from '../useChat'

describe('useChat', () => {
  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useChat())
    
    expect(result.current.messages).toEqual([])
    expect(result.current.isLoading).toBe(false)
    expect(result.current.canSendMessage).toBe(true)
    expect(result.current.error).toBe(null)
  })

  it('should add a message', () => {
    const { result } = renderHook(() => useChat())
    
    act(() => {
      result.current.addMessage({
        text: 'Test message',
        isUser: true
      })
    })
    
    expect(result.current.messages).toHaveLength(1)
    expect(result.current.messages[0].text).toBe('Test message')
    expect(result.current.messages[0].isUser).toBe(true)
  })

  it('should update a message', () => {
    const { result } = renderHook(() => useChat())
    
    let messageId: string
    
    act(() => {
      messageId = result.current.addMessage({
        text: 'Original text',
        isUser: true
      })
    })
    
    act(() => {
      result.current.updateMessage(messageId, {
        text: 'Updated text'
      })
    })
    
    expect(result.current.messages[0].text).toBe('Updated text')
  })

  it('should delete a message', () => {
    const { result } = renderHook(() => useChat())
    
    let messageId: string
    
    act(() => {
      messageId = result.current.addMessage({
        text: 'Test message',
        isUser: true
      })
    })
    
    expect(result.current.messages).toHaveLength(1)
    
    act(() => {
      result.current.deleteMessage(messageId)
    })
    
    expect(result.current.messages).toHaveLength(0)
  })

  it('should clear all messages', () => {
    const { result } = renderHook(() => useChat())
    
    act(() => {
      result.current.addMessage({ text: 'Message 1', isUser: true })
      result.current.addMessage({ text: 'Message 2', isUser: false })
      result.current.addMessage({ text: 'Message 3', isUser: true })
    })
    
    expect(result.current.messages).toHaveLength(3)
    
    act(() => {
      result.current.clearMessages()
    })
    
    expect(result.current.messages).toHaveLength(0)
  })

  it('should set loading state', () => {
    const { result } = renderHook(() => useChat())
    
    expect(result.current.isLoading).toBe(false)
    
    act(() => {
      result.current.setLoading(true)
    })
    
    expect(result.current.isLoading).toBe(true)
    
    act(() => {
      result.current.setLoading(false)
    })
    
    expect(result.current.isLoading).toBe(false)
  })

  it('should set error state', () => {
    const { result } = renderHook(() => useChat())
    
    expect(result.current.error).toBe(null)
    
    act(() => {
      result.current.setError('Test error')
    })
    
    expect(result.current.error).toBe('Test error')
    
    act(() => {
      result.current.setError(null)
    })
    
    expect(result.current.error).toBe(null)
  })

  it('should set canSendMessage state', () => {
    const { result } = renderHook(() => useChat())
    
    expect(result.current.canSendMessage).toBe(true)
    
    act(() => {
      result.current.setCanSendMessage(false)
    })
    
    expect(result.current.canSendMessage).toBe(false)
    
    act(() => {
      result.current.setCanSendMessage(true)
    })
    
    expect(result.current.canSendMessage).toBe(true)
  })

  it('should add multiple messages and maintain order', () => {
    const { result } = renderHook(() => useChat())
    
    act(() => {
      result.current.addMessage({ text: 'First', isUser: true })
      result.current.addMessage({ text: 'Second', isUser: false })
      result.current.addMessage({ text: 'Third', isUser: true })
    })
    
    expect(result.current.messages).toHaveLength(3)
    expect(result.current.messages[0].text).toBe('First')
    expect(result.current.messages[1].text).toBe('Second')
    expect(result.current.messages[2].text).toBe('Third')
  })

  it('should assign unique IDs to messages', () => {
    const { result } = renderHook(() => useChat())
    
    let id1 = ''
    let id2 = ''
    let id3 = ''
    
    act(() => {
      id1 = result.current.addMessage({ text: 'Message 1', isUser: true })
      id2 = result.current.addMessage({ text: 'Message 2', isUser: false })
      id3 = result.current.addMessage({ text: 'Message 3', isUser: true })
    })
    
    expect(id1).not.toBe(id2)
    expect(id2).not.toBe(id3)
    expect(id1).not.toBe(id3)
  })

  it('should add timestamps to messages', () => {
    const { result } = renderHook(() => useChat())
    
    const beforeTime = new Date()
    
    act(() => {
      result.current.addMessage({ text: 'Test', isUser: true })
    })
    
    const afterTime = new Date()
    
    expect(result.current.messages[0].timestamp).toBeDefined()
    expect(result.current.messages[0].timestamp.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime())
    expect(result.current.messages[0].timestamp.getTime()).toBeLessThanOrEqual(afterTime.getTime())
  })

  it('should handle metadata correctly', () => {
    const { result } = renderHook(() => useChat('test-chat-id'))
    
    expect(result.current.metadata.id).toBe('test-chat-id')
    expect(result.current.metadata.isActive).toBe(true)
    expect(result.current.metadata.messageCount).toBe(0)
    
    act(() => {
      result.current.addMessage({ text: 'Test', isUser: true })
    })
    
    expect(result.current.metadata.messageCount).toBe(1)
  })
})
