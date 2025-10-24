import * as React from 'react'
import { Button } from '@/components/ui/button'

interface ReportIssueButtonProps {
  messageId: string
  question: string
  response: string
  onReport: (data: ReportData) => void
  className?: string
}

export interface ReportData {
  messageId: string
  question: string
  response: string
  reportedBy?: string
  timestamp: Date
}

export const ReportIssueButton: React.FC<ReportIssueButtonProps> = ({
  messageId,
  question,
  response,
  onReport,
  className
}) => {
  const [isReporting, setIsReporting] = React.useState(false)
  const [showConfirmation, setShowConfirmation] = React.useState(false)

  const handleReport = () => {
    setIsReporting(true)
    
    const reportData: ReportData = {
      messageId,
      question,
      response,
      reportedBy: 'student@ksu.edu', // In production, get from auth
      timestamp: new Date()
    }

    // Simulate API call
    setTimeout(() => {
      onReport(reportData)
      setIsReporting(false)
      setShowConfirmation(true)
      
      // Hide confirmation after 3 seconds
      setTimeout(() => {
        setShowConfirmation(false)
      }, 3000)
    }, 500)
  }

  if (showConfirmation) {
    return (
      <div className={`text-xs text-green-600 flex items-center gap-1 ${className || ''}`}>
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
        Issue reported
      </div>
    )
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleReport}
      disabled={isReporting}
      className={`text-xs h-6 px-2 text-muted-foreground hover:text-foreground ${className || ''}`}
    >
      <svg 
        className="w-3 h-3 mr-1" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" 
        />
      </svg>
      {isReporting ? 'Reporting...' : 'Report Issue'}
    </Button>
  )
}