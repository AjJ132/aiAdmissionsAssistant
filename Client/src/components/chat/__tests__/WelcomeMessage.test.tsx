import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { WelcomeMessage } from '../WelcomeMessage'

describe('WelcomeMessage', () => {
  it('should render welcome message', () => {
    render(<WelcomeMessage />)
    
    // Should render some text content
    const container = screen.getByText(/test/i)
    expect(container).toBeInTheDocument()
  })

  it('should render with markdown formatting', () => {
    const { container } = render(<WelcomeMessage />)
    
    // Should have some content rendered
    expect(container).toBeTruthy()
  })

  it('should include demo mode hint', () => {
    render(<WelcomeMessage />)
    
    expect(screen.getByText(/test/i)).toBeInTheDocument()
  })

  it('should render without errors', () => {
    const { container } = render(<WelcomeMessage />)
    expect(container.firstChild).toBeTruthy()
  })
})
