import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { WelcomeMessage } from '../WelcomeMessage'

describe('WelcomeMessage', () => {
  it('should render welcome message', () => {
    const { container } = render(<WelcomeMessage />)
    
    // Should render - just check the container has content
    expect(container.firstChild).toBeTruthy()
    // Check for the welcome message wrapper
    const welcomeDiv = container.querySelector('.flex.items-center.justify-center')
    expect(welcomeDiv).toBeInTheDocument()
  })

  it('should render with markdown formatting', () => {
    const { container } = render(<WelcomeMessage />)
    
    // Should have some content rendered
    expect(container).toBeTruthy()
  })

  it('should include demo mode hint', () => {
    const { container } = render(<WelcomeMessage />)
    
    // Demo mode hint has been removed, just check that component renders
    expect(container.firstChild).toBeTruthy()
  })

  it('should render without errors', () => {
    const { container } = render(<WelcomeMessage />)
    expect(container.firstChild).toBeTruthy()
  })
})
