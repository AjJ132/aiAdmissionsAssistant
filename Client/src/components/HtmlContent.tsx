import { useEffect, useState, useRef } from 'react';

interface HtmlContentProps {
  htmlUrl: string;
  onContentLoaded?: () => void;
}

export const HtmlContent: React.FC<HtmlContentProps> = ({ htmlUrl, onContentLoaded }) => {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadHtmlContent = async () => {
      try {
        setLoading(true);
        const response = await fetch(htmlUrl);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch HTML: ${response.statusText}`);
        }
        
        const html = await response.text();
        
        // Extract body content more robustly
        const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
        const bodyContent = bodyMatch ? bodyMatch[1] : html;
        
        // Clean up the content - remove all script/link/style tags since we handle events in React
        const cleanContent = bodyContent
          .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '') // Remove all scripts
          .replace(/<link[^>]*>/gi, '')
          .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
        
        setHtmlContent(cleanContent);
        onContentLoaded?.();
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load HTML content');
      } finally {
        setLoading(false);
      }
    };

    loadHtmlContent();
  }, [htmlUrl, onContentLoaded]);

  // Add event listener for AI chat button after content is loaded
  useEffect(() => {
    if (!htmlContent || !containerRef.current) return;

    const chatButton = containerRef.current.querySelector('#ai-chat-button') as HTMLButtonElement;
    
    if (chatButton) {
      // Add hover effects
      const handleMouseEnter = () => {
        chatButton.style.backgroundColor = '#e6b800';
        chatButton.style.transform = 'translateY(-2px)';
        chatButton.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
      };
      
      const handleMouseLeave = () => {
        chatButton.style.backgroundColor = '#ffc72c';
        chatButton.style.transform = 'translateY(0)';
        chatButton.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
      };
      
      const handleClick = () => {
        // Dispatch a custom event that the React app can listen to
        window.dispatchEvent(new CustomEvent('openAIChat'));
      };

      chatButton.addEventListener('mouseenter', handleMouseEnter);
      chatButton.addEventListener('mouseleave', handleMouseLeave);
      chatButton.addEventListener('click', handleClick);

      // Cleanup function
      return () => {
        chatButton.removeEventListener('mouseenter', handleMouseEnter);
        chatButton.removeEventListener('mouseleave', handleMouseLeave);
        chatButton.removeEventListener('click', handleClick);
      };
    }
  }, [htmlContent]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>Error loading content: {error}</p>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="html-content-container"
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
};
