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

    expect(screen.getByPlaceholderText(/ask me anything about graduate admissions/i)).toBeInTheDocument()
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
    
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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

    const input = screen.getByPlaceholderText(/ask me anything about graduate admissions/i)
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
})
