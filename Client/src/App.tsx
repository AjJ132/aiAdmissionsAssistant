import { useState, useEffect } from 'react'
import './App.css'
import { useExternalResources } from './hooks/useExternalResources'
import { HtmlContent } from './components/HtmlContent'
import { ChatSidebar } from './components/ChatSidebar'
import { DemoChatProvider } from './providers'

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatWidth, setChatWidth] = useState(500);
  const { loaded: resourcesLoaded, error: resourceError } = useExternalResources();

  // Get demo mode from URL parameters (defaults to true)
  // Usage: ?demoMode=false to enable live mode, ?demoMode=true or no param for demo mode
  const getDemoModeFromURL = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const demoModeParam = urlParams.get('demoMode');
    return demoModeParam !== 'false'; // Default to true unless explicitly set to false
  };

  const [useDemoMode, setUseDemoMode] = useState(getDemoModeFromURL);

  // Listen for URL parameter changes
  useEffect(() => {
    const handleURLChange = () => {
      setUseDemoMode(getDemoModeFromURL());
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
    const favicon = document.querySelector("link[rel~='icon']") as HTMLLinkElement;
    if (favicon) {
      favicon.href = "https://www.kennesaw.edu/webstatic/_omni/images/favicon.ico";
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
      <DemoChatProvider>
        {(chat) => (
          <ChatSidebar 
            isOpen={isChatOpen}
            onToggle={handleChatToggle}
            onWidthChange={handleChatWidthChange}
            isDemoMode={useDemoMode}
            chatProvider={chat}
          />
        )}
      </DemoChatProvider>
      
    </div>
  )
}

export default App