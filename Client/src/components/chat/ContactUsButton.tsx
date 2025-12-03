import React, { useState } from 'react';
import { Phone, Mail, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ContactUsButtonProps {
  className?: string;
}

export const ContactUsButton: React.FC<ContactUsButtonProps> = ({ className = '' }) => {
  const [showContacts, setShowContacts] = useState(false);

  const gradAdmissionsEmail = 'graduate@kennesaw.edu';
  const gradAdmissionsPhone = '470-578-4377';

  const toggleContacts = () => {
    setShowContacts(!showContacts);
  };

  return (
    <div className={`relative ${className}`}>
      <Button
        onClick={toggleContacts}
        variant="outline"
        size="sm"
        className="flex items-center gap-2 bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-300"
        aria-label="Contact Graduate Admissions"
      >
        <Phone className="w-4 h-4" />
        <span>Contact Us</span>
      </Button>

      {showContacts && (
        <div className="absolute bottom-full mb-2 left-0 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[280px] z-50">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-900 text-sm">Graduate Admissions</h3>
            <button
              onClick={toggleContacts}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              aria-label="Close contact info"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>

          <div className="space-y-3">
            <a
              href={`mailto:${gradAdmissionsEmail}`}
              className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 transition-colors group"
            >
              <div className="p-2 bg-blue-50 rounded-full group-hover:bg-blue-100 transition-colors">
                <Mail className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <div className="text-xs text-gray-500">Email</div>
                <div className="text-sm text-blue-600 hover:underline">{gradAdmissionsEmail}</div>
              </div>
            </a>

            <a
              href={`tel:${gradAdmissionsPhone}`}
              className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 transition-colors group"
            >
              <div className="p-2 bg-green-50 rounded-full group-hover:bg-green-100 transition-colors">
                <Phone className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <div className="text-xs text-gray-500">Phone</div>
                <div className="text-sm text-green-600 hover:underline">{gradAdmissionsPhone}</div>
              </div>
            </a>
          </div>
        </div>
      )}
    </div>
  );
};
