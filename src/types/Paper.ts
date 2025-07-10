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
    technicalInnovation: string;
    methodologyBreakdown: string;
    performanceHighlights: string;
    implementationInsights: string;
    researchContext: string;
    futureImplications: string;
    limitations: string;
    impactScore: number;
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
    readingTime: number;
    hasCode: boolean;
    implementationComplexity: 'low' | 'medium' | 'high';
    practicalApplicability: 'low' | 'medium' | 'high';
    researchSignificance: 'incremental' | 'significant' | 'breakthrough';
    reproductionDifficulty: 'low' | 'medium' | 'high';
  };
  link: string;
}