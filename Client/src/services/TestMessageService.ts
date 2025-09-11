export interface TestMessage {
  userMessage: {
    text: string;
    isUser: true;
  };
  response: string;
  sources: string[];
}

export class TestMessageService {
  private static instance: TestMessageService;
  
  public static getInstance(): TestMessageService {
    if (!TestMessageService.instance) {
      TestMessageService.instance = new TestMessageService();
    }
    return TestMessageService.instance;
  }

  public getTestMessage(): TestMessage {
    const testUserMessage = {
      text: "What are the admission requirements for the Computer Science graduate program?",
      isUser: true as const,
    };

    const testResponse = `# Computer Science Graduate Program Requirements

Based on my search of the latest information, here are the admission requirements for the Computer Science graduate program at Kennesaw State University:

## 📋 General Requirements

- **Bachelor's degree** from an accredited institution
- **Minimum GPA** of 2.75 (4.0 scale) for regular admission
- **Official transcripts** from all institutions attended

## 🎯 Program-Specific Requirements

- Undergraduate degree in Computer Science or related field
- Prerequisites in:
  - Programming fundamentals
  - Data structures and algorithms
  - Computer organization
- **GRE scores** (recommended but not required for some tracks)
- **Statement of purpose** outlining academic and career goals
- **Two letters of recommendation**

## 📅 Application Deadlines

| Semester | Deadline | Priority Consideration |
|----------|----------|----------------------|
| Fall | July 1st | March 1st |
| Spring | November 1st | September 1st |
| Summer | April 1st | February 1st |

## 🚀 Program Options

The program offers both **thesis** and **non-thesis** options, with specializations in:

> **Popular Specializations:**
> - Cybersecurity & Information Assurance
> - Data Science & Analytics
> - Software Engineering
> - Machine Learning & AI

### 💡 Pro Tips for Application

1. **Start early** - Give yourself 6-8 weeks before the deadline
2. **Contact faculty** - Reach out to potential advisors
3. **Prepare for interviews** - Some tracks require interviews
4. **Check prerequisites** - Ensure you meet all course requirements

For more detailed information, visit the [Computer Science Department](https://ccse.kennesaw.edu/cs/) website or contact the graduate admissions office.`;

    const sources = [
      "Kennesaw State University Graduate Admissions",
      "Computer Science Department Requirements",
      "Graduate Catalog 2024-2025"
    ];

    return {
      userMessage: testUserMessage,
      response: testResponse,
      sources
    };
  }
}
