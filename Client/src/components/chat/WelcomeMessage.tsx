import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const welcomeMessages = [
  "🌟 **Ready to help** you navigate your graduate admissions journey!",
  "🎓 Let's explore your **academic future** together!",
  "✨ Your path to graduate school starts with a **single question**...",
  "🚀 Welcome! \n I'm here to make your admissions process **smoother**.",
  "💡 Ask me anything \n - from **application tips** to **program details**!",
  "🎯 Let's turn your **graduate school dreams** \n into reality!"
];

export const WelcomeMessage: React.FC = () => {
  const [selectedMessage, setSelectedMessage] = useState('');

  useEffect(() => {
    // Select a random message on component mount
    const randomIndex = Math.floor(Math.random() * welcomeMessages.length);
    setSelectedMessage(welcomeMessages[randomIndex]);
  }, []);

  return (
    <div className="flex items-center justify-center h-full min-h-[400px]">
      <div className="text-center px-6">
        <div className="text-gray-400 text-sm font-light opacity-70 leading-relaxed prose prose-xs max-w-none">
            <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({children}) => <p className="text-lg mb-0 font-medium">{children}</p>,
                    strong: ({children}) => <strong className="font-bold text-primary">{children}</strong>,
                  }}
                >
                  {selectedMessage}
              </ReactMarkdown>

            <p>
              Type "test" to see an example response (demo mode)
            </p>
        </div>
      </div>
    </div>
  );
};
