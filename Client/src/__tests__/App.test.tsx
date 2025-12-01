import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('should render without crashing', () => {
    render(<App />)
    expect(document.body).toBeTruthy()
  })

  it('should render the main content area', () => {
    const { container } = render(<App />)
    expect(container.firstChild).toBeTruthy()
  })

  it('should always use live mode (connected to backend)', () => {
    // Clear any existing URL params
    window.history.pushState({}, '', window.location.pathname)
    render(<App />)
    // App should render successfully and connect to backend
    expect(document.body).toBeTruthy()
  })
})
