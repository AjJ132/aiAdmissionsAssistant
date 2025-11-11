import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MessageInput } from '../MessageInput'

describe('MessageInput', () => {
  const mockOnSendMessage = vi.fn()

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render input field and send button', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    expect(screen.getByPlaceholderText(/message ksu chatbot/i)).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('should allow typing in the input field', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    await user.type(input, 'Hello test message')
    
    expect(input).toHaveValue('Hello test message')
  })

  it('should send message when button is clicked', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    const button = screen.getByRole('button')
    
    await user.type(input, 'Test message')
    await user.click(button)

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message')
    expect(input).toHaveValue('')
  })

  it('should send message when Enter key is pressed', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    
    await user.type(input, 'Test message{Enter}')

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message')
    expect(input).toHaveValue('')
  })

  it('should not send empty messages', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    const button = screen.getByRole('button')
    
    await user.type(input, '   ')
    await user.click(button)

    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('should trim whitespace from messages', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    const button = screen.getByRole('button')
    
    await user.type(input, '  Test message  ')
    await user.click(button)

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message')
  })

  it('should disable input when isLoading is true', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={true}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    expect(input).toBeDisabled()
  })

  it('should disable input when canSendMessage is false', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={false}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    expect(input).toBeDisabled()
  })

  it('should disable send button when input is empty', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('should disable send button when isLoading is true', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={true}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    await user.type(input, 'Test')

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('should use custom placeholder when provided', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
        placeholder="Custom placeholder text"
      />
    )

    expect(screen.getByPlaceholderText('Custom placeholder text')).toBeInTheDocument()
  })

  it('should enforce maximum character limit of 500', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i) as HTMLTextAreaElement
    const longText = 'a'.repeat(600) // Try to type 600 characters
    
    await user.type(input, longText)
    
    // Should be limited to 500 characters due to maxLength attribute
    expect(input.value.length).toBeLessThanOrEqual(500)
  })

  it('should display character counter', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    // Should show 0/500 initially
    expect(screen.getByText('0/500')).toBeInTheDocument()
  })

  it('should update character counter as user types', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    await user.type(input, 'Hello')
    
    expect(screen.getByText('5/500')).toBeInTheDocument()
  })

  it('should not send messages longer than 500 characters', async () => {
    const user = userEvent.setup()
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        isLoading={false}
        canSendMessage={true}
      />
    )

    const input = screen.getByPlaceholderText(/message ksu chatbot/i)
    const button = screen.getByRole('button')
    
    // Manually set a value longer than 500 (bypassing maxLength for testing)
    const longText = 'a'.repeat(501)
    Object.defineProperty(input, 'value', {
      writable: true,
      value: longText
    })
    
    await user.click(button)

    // Should not send the message
    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })
})
