/// <reference types="vitest" />
import '@testing-library/jest-dom'

declare global {
  namespace Vi {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    interface Matchers<R = any> {
      toBeInTheDocument(): R
      toHaveClass(...classes: string[]): R
      toBeDisabled(): R
      toBeEnabled(): R
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      toHaveValue(value: any): R
      toHaveTextContent(text: string | RegExp): R
    }
  }
}
