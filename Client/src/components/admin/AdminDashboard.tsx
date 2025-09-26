import * as React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardAction } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

interface ChatResponse {
  id: string
  timestamp: Date
  question: string
  originalResponse: string
  correctedResponse?: string
  status: 'pending' | 'corrected' | 'approved'
  reportedBy?: string
  category?: string
}

interface AdminDashboardProps {
  className?: string
  onClose?: () => void
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ className, onClose }) => {
  // Mock data for demonstration
  const [responses, setResponses] = React.useState<ChatResponse[]>([
    {
      id: '1',
      timestamp: new Date('2024-09-25T10:30:00'),
      question: 'What is the deadline for graduate applications?',
      originalResponse: 'The deadline is March 1st for all programs.',
      status: 'pending',
      reportedBy: 'student@ksu.edu',
      category: 'Deadlines'
    },
    {
      id: '2', 
      timestamp: new Date('2024-09-25T11:15:00'),
      question: 'What GPA do I need for the MBA program?',
      originalResponse: 'You need a minimum GPA of 2.5.',
      correctedResponse: 'You need a minimum GPA of 3.0 for the MBA program at KSU.',
      status: 'corrected',
      category: 'Requirements'
    },
    {
      id: '3',
      timestamp: new Date('2024-09-25T12:45:00'),
      question: 'How do I submit my transcripts?',
      originalResponse: 'Send transcripts by mail to the admissions office.',
      correctedResponse: 'Submit official transcripts electronically through the National Student Clearinghouse or by mail to the Graduate Admissions Office.',
      status: 'approved',
      category: 'Application Process'
    }
  ])

  const [selectedResponse, setSelectedResponse] = React.useState<ChatResponse | null>(null)
  const [correctionText, setCorrectionText] = React.useState('')
  const [searchQuery, setSearchQuery] = React.useState('')

  const handleSelectResponse = (response: ChatResponse) => {
    setSelectedResponse(response)
    setCorrectionText(response.correctedResponse || response.originalResponse)
  }

  const handleSaveCorrection = () => {
    if (!selectedResponse) return

    setResponses(prev => prev.map(r => 
      r.id === selectedResponse.id 
        ? { ...r, correctedResponse: correctionText, status: 'corrected' as const }
        : r
    ))

    setSelectedResponse(null)
    setCorrectionText('')
  }

  const handleApproveCorrection = (responseId: string) => {
    setResponses(prev => prev.map(r => 
      r.id === responseId ? { ...r, status: 'approved' as const } : r
    ))
  }

  const filteredResponses = responses.filter(response =>
    response.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    response.originalResponse.toLowerCase().includes(searchQuery.toLowerCase()) ||
    response.category?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getStatusColor = (status: ChatResponse['status']) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-50'
      case 'corrected': return 'text-blue-600 bg-blue-50'
      case 'approved': return 'text-green-600 bg-green-50'
    }
  }

  return (
    <div className={`flex h-screen bg-background ${className || ''}`}>
      {/* Sidebar - Response List */}
      <div className="w-1/3 border-r border-border flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Chatbot Admin Dashboard</h1>
            {onClose && (
              <Button variant="ghost" size="icon" onClick={onClose}>
                ✕
              </Button>
            )}
          </div>
          
          <Input
            placeholder="Search responses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="mb-4"
          />

          {/* Stats */}
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center p-2 rounded bg-yellow-50">
              <div className="font-semibold text-yellow-800">
                {responses.filter(r => r.status === 'pending').length}
              </div>
              <div className="text-yellow-600">Pending</div>
            </div>
            <div className="text-center p-2 rounded bg-blue-50">
              <div className="font-semibold text-blue-800">
                {responses.filter(r => r.status === 'corrected').length}
              </div>
              <div className="text-blue-600">Corrected</div>
            </div>
            <div className="text-center p-2 rounded bg-green-50">
              <div className="font-semibold text-green-800">
                {responses.filter(r => r.status === 'approved').length}
              </div>
              <div className="text-green-600">Approved</div>
            </div>
          </div>
        </div>

        {/* Response List */}
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-3">
            {filteredResponses.map((response) => (
              <Card
                key={response.id}
                className={`cursor-pointer transition-colors hover:bg-accent/50 ${
                  selectedResponse?.id === response.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => handleSelectResponse(response)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm line-clamp-2">
                      {response.question}
                    </CardTitle>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(response.status)}`}>
                      {response.status}
                    </span>
                  </div>
                  <CardDescription className="text-xs">
                    {response.timestamp.toLocaleString()}
                    {response.category && ` • ${response.category}`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {response.originalResponse}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main Content - Correction Interface */}
      <div className="flex-1 flex flex-col">
        {selectedResponse ? (
          <>
            {/* Response Header */}
            <div className="p-6 border-b border-border">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold mb-2">Response Correction</h2>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{selectedResponse.timestamp.toLocaleString()}</span>
                    <Separator orientation="vertical" className="h-4" />
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(selectedResponse.status)}`}>
                      {selectedResponse.status}
                    </span>
                    {selectedResponse.category && (
                      <>
                        <Separator orientation="vertical" className="h-4" />
                        <span>{selectedResponse.category}</span>
                      </>
                    )}
                  </div>
                </div>
                
                {selectedResponse.status === 'corrected' && (
                  <Button 
                    variant="default" 
                    size="sm"
                    onClick={() => handleApproveCorrection(selectedResponse.id)}
                  >
                    Approve Correction
                  </Button>
                )}
              </div>
            </div>

            {/* Content Area */}
            <ScrollArea className="flex-1">
              <div className="p-6 space-y-6">
                {/* Original Question */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Student Question</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{selectedResponse.question}</p>
                  </CardContent>
                </Card>

                {/* Original Response */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      Original Chatbot Response
                      <span className="px-2 py-1 rounded text-xs bg-red-50 text-red-600 font-medium">
                        Needs Correction
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm bg-red-50 p-3 rounded border">
                      {selectedResponse.originalResponse}
                    </p>
                  </CardContent>
                </Card>

                {/* Correction Interface */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Corrected Response</CardTitle>
                    <CardDescription>
                      Edit the response below to provide accurate information for future similar queries.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      value={correctionText}
                      onChange={(e) => setCorrectionText(e.target.value)}
                      placeholder="Enter the corrected response..."
                      className="min-h-32"
                    />
                    
                    <div className="flex justify-between items-center">
                      <div className="text-xs text-muted-foreground">
                        This correction will be used to improve future responses on similar topics.
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            setSelectedResponse(null)
                            setCorrectionText('')
                          }}
                        >
                          Cancel
                        </Button>
                        <Button 
                          variant="default" 
                          size="sm"
                          onClick={handleSaveCorrection}
                          disabled={!correctionText.trim() || correctionText === selectedResponse.originalResponse}
                        >
                          Save Correction
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Additional Info */}
                {selectedResponse.reportedBy && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Report Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3 text-sm">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="text-xs">
                            {selectedResponse.reportedBy.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span>Reported by: {selectedResponse.reportedBy}</span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </ScrollArea>
          </>
        ) : (
          /* Empty State */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-sm">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="text-lg font-semibold mb-2">Select a Response to Review</h3>
              <p className="text-muted-foreground text-sm">
                Choose a chatbot response from the sidebar to review and correct any inaccuracies.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminDashboard