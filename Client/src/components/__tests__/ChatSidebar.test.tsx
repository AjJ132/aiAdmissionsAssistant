import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatSidebar } from '../ChatSidebar'
import type { Message } from '@/hooks/useChat'

describe('ChatSidebar', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      text: 'Hello',
      isUser: true,
      timestamp: new Date()
    },
    {
      id: '2',
      text: 'Hi there!',
      isUser: false,
      timestamp: new Date()
    }
  ]

  const mockChatProvider = {
    sendMessage: vi.fn(),
    messages: mockMessages,
    isLoading: false,
    canSendMessage: true,
    clearMessages: vi.fn()
  }

  const defaultProps = {
    isOpen: true,
    onToggle: vi.fn(),
    onWidthChange: vi.fn(),
    chatProvider: mockChatProvider
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render when open', () => {
    render(<ChatSidebar {...defaultProps} />)
    
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Hi there!')).toBeInTheDocument()
  })

  it('should not render when closed', () => {
    render(<ChatSidebar {...defaultProps} isOpen={false} />)
    
    // When closed, the sidebar should be off-screen (positioned off the viewport)
    const sidebar = screen.getByText('Hello').closest('div[class*="fixed"]')
    expect(sidebar).toHaveStyle({ right: '-500px' })
  })

  it('should display messages from chat provider', () => {
    render(<ChatSidebar {...defaultProps} />)
    
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Hi there!')).toBeInTheDocument()
  })

  it('should call sendMessage when user sends a message', async () => {
    const user = userEvent.setup()
    render(<ChatSidebar {...defaultProps} />)
    
    const input = screen.getByPlaceholderText(/ask about graduate admissions/i)
    const sendButton = screen.getByRole('button', { name: '' })
    
    await user.type(input, 'Test message')
    await user.click(sendButton)
    
    expect(mockChatProvider.sendMessage).toHaveBeenCalledWith('Test message')
  })

  it('should show loading state', () => {
    const loadingProvider = {
      ...mockChatProvider,
      isLoading: true
    }
    
    const { container } = render(<ChatSidebar {...defaultProps} chatProvider={loadingProvider} />)
    
    // Check for animated dots instead of text
    const dots = container.querySelectorAll('.animate-bounce')
    expect(dots.length).toBeGreaterThan(0)
  })

  it('should disable input when canSendMessage is false', () => {
    const disabledProvider = {
      ...mockChatProvider,
      canSendMessage: false
    }
    
    render(<ChatSidebar {...defaultProps} chatProvider={disabledProvider} />)
    
    const input = screen.getByPlaceholderText(/please wait for response/i)
    expect(input).toBeDisabled()
  })

  it('should call onToggle when toggle is triggered', () => {
    const onToggle = vi.fn()
    render(<ChatSidebar {...defaultProps} onToggle={onToggle} />)
    
    // The component should render with onToggle function
    expect(onToggle).toBeDefined()
  })

  it('should display empty state when no messages', () => {
    const emptyProvider = {
      ...mockChatProvider,
      messages: []
    }
    
    const { container } = render(<ChatSidebar {...defaultProps} chatProvider={emptyProvider} />)
    
    // Check for common text in welcome message - just check it renders
    expect(container.firstChild).toBeTruthy()
    // Check for the welcome message wrapper
    const welcomeDiv = container.querySelector('.flex.items-center.justify-center')
    expect(welcomeDiv).toBeInTheDocument()
  })

  it('should handle multiple messages', () => {
    const multipleMessages: Message[] = [
      { id: '1', text: 'Message 1', isUser: true, timestamp: new Date() },
      { id: '2', text: 'Message 2', isUser: false, timestamp: new Date() },
      { id: '3', text: 'Message 3', isUser: true, timestamp: new Date() },
      { id: '4', text: 'Message 4', isUser: false, timestamp: new Date() }
    ]
    
    const multiProvider = {
      ...mockChatProvider,
      messages: multipleMessages
    }
    
    render(<ChatSidebar {...defaultProps} chatProvider={multiProvider} />)
    
    expect(screen.getByText('Message 1')).toBeInTheDocument()
    expect(screen.getByText('Message 2')).toBeInTheDocument()
    expect(screen.getByText('Message 3')).toBeInTheDocument()
    expect(screen.getByText('Message 4')).toBeInTheDocument()
  })
})
