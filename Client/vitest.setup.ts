import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Cleanup after each test case
afterEach(() => {
  cleanup()
})

// Mock scrollIntoView which is not implemented in jsdom
Element.prototype.scrollIntoView = function() {
  // No-op for tests
}
