import { useState, useEffect } from 'react'
import './App.css'
import { useExternalResources } from './hooks/useExternalResources'
import { HtmlContent } from './components/HtmlContent'
import { ChatSidebar } from './components/ChatSidebar'
import AdminDashboard from './components/admin/AdminDashboard'
import { Button } from './components/ui/button'
import { LiveChatProvider } from './providers'

// Backend API endpoint from environment variable
// This should be set in Amplify environment variables as VITE_API_ENDPOINT
// Example: https://abc123.execute-api.us-east-1.amazonaws.com/chat
const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || '/api/chat'

// Log configuration on startup
console.log('Chat API Endpoint:', API_ENDPOINT)

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatWidth, setChatWidth] = useState(500);
  const { loaded: resourcesLoaded, error: resourceError } = useExternalResources();

  // Get admin mode from URL parameters
  // Usage: ?admin=true to show admin dashboard
  const getAdminModeFromURL = () => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('admin') === 'true';
  };

  const [showAdminDashboard, setShowAdminDashboard] = useState(getAdminModeFromURL);

  // Listen for URL parameter changes
  useEffect(() => {
    const handleURLChange = () => {
      setShowAdminDashboard(getAdminModeFromURL());
    };

    // Listen for popstate events (back/forward navigation)
    window.addEventListener('popstate', handleURLChange);
    
    // Also listen for custom events if URL changes programmatically
    window.addEventListener('urlchange', handleURLChange);

    return () => {
      window.removeEventListener('popstate', handleURLChange);
      window.removeEventListener('urlchange', handleURLChange);
    };
  }, []);

  // Set favicon
  useEffect(() => {
    const faviconURL = 'scrappyhead.png';
    const favicon = document.querySelector("link[rel~='icon']") as HTMLLinkElement | null;
    if (favicon) {
      favicon.href = faviconURL;
    } else {
      const newFavicon = document.createElement('link');
      newFavicon.rel = 'icon';
      newFavicon.type = 'image/png';
      newFavicon.href = "https://www.kennesaw.edu/webstatic/_omni/images/favicon.ico";
      document.head.appendChild(newFavicon);
    }
  }, []);

  // Listen for AI chat button clicks from HTML
  useEffect(() => {
    const handleOpenAIChat = () => {
      setIsChatOpen(true);
    };

    window.addEventListener('openAIChat', handleOpenAIChat);
    
    return () => {
      window.removeEventListener('openAIChat', handleOpenAIChat);
    };
  }, []);

  const handleContentLoaded = () => {
    // HTML content loaded successfully
  };

  const handleChatToggle = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleChatWidthChange = (width: number) => {
    setChatWidth(width);
  };

  const toggleAdminDashboard = () => {
    const newShowAdmin = !showAdminDashboard;
    setShowAdminDashboard(newShowAdmin);
    
    // Update URL to reflect admin mode
    const url = new URL(window.location.href);
    if (newShowAdmin) {
      url.searchParams.set('admin', 'true');
    } else {
      url.searchParams.delete('admin');
    }
    window.history.pushState({}, '', url);
  };

  const handleAdminClose = () => {
    setShowAdminDashboard(false);
    
    // Update URL to reflect admin mode
    const url = new URL(window.location.href);
    url.searchParams.delete('admin');
    window.history.pushState({}, '', url);
  };

  if (!resourcesLoaded && !resourceError) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">
          <div>Loading external resources...</div>
        </div>
      </div>
    );
  }

  if (resourceError) {
    return (
      <div className="error-container">
        <div className="error-message">
          <h2>Error Loading Resources</h2>
          <p>{resourceError}</p>
          <p>Some external resources may not be available. The page may not display correctly.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Admin Toggle Button - Grey secondary button, positioned below nav */}
      {!showAdminDashboard && (
        <Button
          onClick={toggleAdminDashboard}
          className="fixed top-[68px] right-6 z-[1000] shadow-md hover:shadow-lg transition-all duration-200"
          variant="secondary"
          size="sm"
        >
          <svg 
            className="w-4 h-4 mr-1.5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" 
            />
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
            />
          </svg>
          Chatbot Admin
        </Button>
      )}

      {/* Conditional Content */}
      {showAdminDashboard ? (
        /* Admin Dashboard Mode */
        <AdminDashboard 
          onClose={handleAdminClose}
          className="h-screen"
        />
      ) : (
        /* Normal Mode */
        <>
          {/* Main content from HTML */}
          <div 
            className="main-content"
            style={{
              marginRight: isChatOpen ? `${chatWidth}px` : '0',
              transition: 'margin-right 0.2s ease-out'
            }}
          >
            <HtmlContent 
              htmlUrl="/grad_admin.html"
              onContentLoaded={handleContentLoaded}
            />
          </div>
          
          {/* Chat sidebar */}
          <LiveChatProvider apiEndpoint={API_ENDPOINT}>
            {(chat) => (
              <ChatSidebar 
                isOpen={isChatOpen}
                onToggle={handleChatToggle}
                onWidthChange={handleChatWidthChange}
                chatProvider={chat}
              />
            )}
          </LiveChatProvider>
        </>
      )}
    </div>
  )
}

export default App