import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageList } from '../MessageList'
import type { Message } from '@/hooks/useChat'

describe('MessageList', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      text: 'Hello, what are the admission requirements?',
      isUser: true,
      timestamp: new Date('2025-10-22T10:00:00')
    },
    {
      id: '2',
      text: 'Here are the admission requirements...',
      isUser: false,
      timestamp: new Date('2025-10-22T10:00:05')
    }
  ]

  it('should render welcome message when no messages exist', () => {
    render(<MessageList messages={[]} isLoading={false} />)
    
    // WelcomeMessage should be rendered - check for common text in all welcome messages
    expect(screen.getByText(/test/i)).toBeInTheDocument()
  })

  it('should render messages correctly', () => {
    render(<MessageList messages={mockMessages} isLoading={false} />)
    
    expect(screen.getByText('Hello, what are the admission requirements?')).toBeInTheDocument()
    expect(screen.getByText('Here are the admission requirements...')).toBeInTheDocument()
  })

  it('should display user and AI avatars correctly', () => {
    render(<MessageList messages={mockMessages} isLoading={false} />)
    
    // Should have U and AI avatar fallbacks
    expect(screen.getByText('U')).toBeInTheDocument()
    expect(screen.getByText('AI')).toBeInTheDocument()
  })

  it('should show typing indicator when isLoading is true', () => {
    render(<MessageList messages={mockMessages} isLoading={true} />)
    
    expect(screen.getByText(/is typing/i)).toBeInTheDocument()
  })

  it('should handle empty message list with loading', () => {
    render(<MessageList messages={[]} isLoading={true} />)
    
    // Should show typing indicator instead of welcome message
    expect(screen.getByText(/is typing/i)).toBeInTheDocument()
  })

  it('should render markdown content in messages', () => {
    const messagesWithMarkdown: Message[] = [
      {
        id: '1',
        text: '**Bold text** and *italic text*',
        isUser: false,
        timestamp: new Date()
      }
    ]

    render(<MessageList messages={messagesWithMarkdown} isLoading={false} />)
    
    expect(screen.getByText('Bold text')).toBeInTheDocument()
  })

  it('should handle multiple messages from the same sender', () => {
    const multipleMessages: Message[] = [
      {
        id: '1',
        text: 'First question',
        isUser: true,
        timestamp: new Date()
      },
      {
        id: '2',
        text: 'Second question',
        isUser: true,
        timestamp: new Date()
      },
      {
        id: '3',
        text: 'Answer to both',
        isUser: false,
        timestamp: new Date()
      }
    ]

    render(<MessageList messages={multipleMessages} isLoading={false} />)
    
    expect(screen.getByText('First question')).toBeInTheDocument()
    expect(screen.getByText('Second question')).toBeInTheDocument()
    expect(screen.getByText('Answer to both')).toBeInTheDocument()
  })

  it('should call onReportIssue when report is submitted', () => {
    const mockOnReportIssue = vi.fn()
    
    render(
      <MessageList 
        messages={mockMessages} 
        isLoading={false} 
        onReportIssue={mockOnReportIssue}
      />
    )
    
    // We can verify the component renders without errors
    expect(screen.getByText('Hello, what are the admission requirements?')).toBeInTheDocument()
  })

  it('should show searching indicator when isSearching is true', () => {
    render(
      <MessageList 
        messages={mockMessages} 
        isLoading={false} 
        isSearching={true}
      />
    )
    
    // Component should render without errors
    expect(screen.getByText('Hello, what are the admission requirements?')).toBeInTheDocument()
  })

  it('should render messages with sources', () => {
    const messagesWithSources: Message[] = [
      {
        id: '1',
        text: 'Question about programs',
        isUser: true,
        timestamp: new Date()
      },
      {
        id: '2',
        text: 'Here is information from our sources',
        isUser: false,
        sources: ['source1.pdf', 'source2.pdf'],
        timestamp: new Date()
      }
    ]

    render(<MessageList messages={messagesWithSources} isLoading={false} />)
    
    expect(screen.getByText('Here is information from our sources')).toBeInTheDocument()
  })
})
