import { useEffect, useState } from 'react';

interface ExternalResource {
  type: 'css' | 'js';
  src: string;
  attributes?: Record<string, string>;
}

const externalResources: ExternalResource[] = [
  // CSS Resources
  {
    type: 'css',
    src: '/graduate-admissions-files/external.min.css',
  },
  {
    type: 'css',
    src: '/graduate-admissions-files/css2.css',
  },
  // JavaScript Resources (only essential ones for functionality)
  {
    type: 'js',
    src: '/graduate-admissions-files/main_new.min.js',
    attributes: { defer: 'true' }
  },
  {
    type: 'js',
    src: '/graduate-admissions-files/dom-slider.js',
    attributes: { defer: 'true' }
  },
  {
    type: 'js',
    src: '/graduate-admissions-files/direct-edit.js'
  },
  {
    type: 'js',
    src: '/graduate-admissions-files/search-script.min.js'
  }
];

export const useExternalResources = () => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadedResources: HTMLElement[] = [];

    const loadResource = (resource: ExternalResource): Promise<void> => {
      return new Promise((resolve, reject) => {
        let element: HTMLElement;

        if (resource.type === 'css') {
          element = document.createElement('link');
          element.setAttribute('rel', 'stylesheet');
          element.setAttribute('type', 'text/css');
          element.setAttribute('href', resource.src);
          
          if (resource.attributes) {
            Object.entries(resource.attributes).forEach(([key, value]) => {
              element.setAttribute(key, value);
            });
          }

          element.onload = () => resolve();
          element.onerror = () => reject(new Error(`Failed to load CSS: ${resource.src}`));
        } else {
          element = document.createElement('script');
          element.setAttribute('src', resource.src);
          element.setAttribute('type', 'text/javascript');
          
          if (resource.attributes) {
            Object.entries(resource.attributes).forEach(([key, value]) => {
              element.setAttribute(key, value);
            });
          }

          element.onload = () => resolve();
          element.onerror = () => reject(new Error(`Failed to load JS: ${resource.src}`));
        }

        loadedResources.push(element);
        document.head.appendChild(element);
      });
    };

    const loadAllResources = async () => {
      try {
        // Load CSS first
        const cssPromises = externalResources
          .filter(r => r.type === 'css')
          .map(loadResource);
        
        await Promise.all(cssPromises);

        // Then load JavaScript
        const jsPromises = externalResources
          .filter(r => r.type === 'js')
          .map(loadResource);
        
        await Promise.all(jsPromises);

        setLoaded(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resources');
      }
    };

    loadAllResources();

    // Cleanup function
    return () => {
      loadedResources.forEach(element => {
        if (element.parentNode) {
          element.parentNode.removeChild(element);
        }
      });
    };
  }, []);

  return { loaded, error };
};
