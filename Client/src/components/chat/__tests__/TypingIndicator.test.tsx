import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TypingIndicator } from '../TypingIndicator'

describe('TypingIndicator', () => {
  it('should render typing indicator', () => {
    render(<TypingIndicator />)
    
    expect(screen.getByText(/is typing/i)).toBeInTheDocument()
  })

  it('should display animated dots', () => {
    const { container } = render(<TypingIndicator />)
    
    // Should have 3 animated dots
    const dots = container.querySelectorAll('.animate-bounce')
    expect(dots.length).toBe(3)
  })

  it('should show avatar fallback', () => {
    render(<TypingIndicator />)
    
    expect(screen.getByText('KSU')).toBeInTheDocument()
  })

  it('should render without errors', () => {
    const { container } = render(<TypingIndicator />)
    expect(container.firstChild).toBeTruthy()
  })
})
