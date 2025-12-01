import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const welcomeMessages = [
  "Ready to help you navigate your graduate admissions journey!",
  "Let's explore your academic future together!",
  "Your path to graduate school starts here...",
  "Welcome! I'm here to make your admissions process smoother.",
  "Ask me anything - from application tips to program details!",
  "Let's turn your graduate school dreams into reality!"
];

export const WelcomeMessage: React.FC = () => {
  const [selectedMessage, setSelectedMessage] = useState('');

  useEffect(() => {
    // Select a random message on component mount
    const randomIndex = Math.floor(Math.random() * welcomeMessages.length);
    setSelectedMessage(welcomeMessages[randomIndex]);
  }, []);

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center px-8 max-w-md">
        <div className="text-gray-400 text-sm leading-relaxed">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({children}) => <p className="mb-0">{children}</p>,
            }}
          >
            {selectedMessage}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
