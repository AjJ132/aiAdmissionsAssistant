export interface MockResponse {
  text: string;
  sources?: string[];
}

export class ResponseService {
  private static instance: ResponseService;
  
  public static getInstance(): ResponseService {
    if (!ResponseService.instance) {
      ResponseService.instance = new ResponseService();
    }
    return ResponseService.instance;
  }

  private readonly mockResponses: string[] = [
    "Thank you for your message! I'm here to help with graduate admissions questions. What specific information are you looking for?",
    "I'd be happy to assist you with graduate admissions. Could you tell me more about your area of interest or specific questions you have?",
    "Great question! For graduate admissions, I can help with:\n\n- **Application requirements**\n- **Deadlines and timelines**\n- **Program information**\n- **Financial aid options**\n\nWhat would you like to know?",
    "I'm here to support your graduate admissions journey. Whether you need help with applications, requirements, or program details, I'm ready to assist!",
    "Welcome! I can help you navigate the graduate admissions process. What specific aspect would you like to explore today?"
  ];

  private readonly mockSources: string[] = [
    "https://www.kennesaw.edu/graduate/admissions/",
    "https://www.kennesaw.edu/graduate/programs/",
    "https://www.kennesaw.edu/graduate/requirements/",
  ];

  public getRandomResponse(): MockResponse {
    const randomResponse = this.mockResponses[Math.floor(Math.random() * this.mockResponses.length)];
    const shouldIncludeSources = Math.random() > 0.5;
    
    return {
      text: randomResponse,
      sources: shouldIncludeSources ? this.mockSources : undefined,
    };
  }

  public getSearchingMessage(): string {
    return "Hello! Yes I can help you find that information. Please let me search my knowledge bases first to get you the most up to date information.";
  }

  public getInitialSearchMessage(): string {
    return "Let me search my knowledge base for the most up-to-date information...";
  }

  public simulateTypingDelay(callback: () => void, delay: number = 1000): void {
    setTimeout(callback, delay);
  }

  public simulateSearchDelay(callback: () => void, delay: number = 2000): void {
    setTimeout(callback, delay);
  }

  public getRandomResponseDelay(): number {
    return Math.random() * 2000 + 1000;
  }
}
