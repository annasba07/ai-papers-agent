export interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  summary: string;
  aiSummary: {
    summary: string;
    keyContribution: string;
    novelty: string;
    impactScore: number;
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
    readingTime: number;
    hasCode: boolean;
    implementationComplexity: 'low' | 'medium' | 'high';
    practicalApplicability: 'low' | 'medium' | 'high';
  };
  link: string;
}