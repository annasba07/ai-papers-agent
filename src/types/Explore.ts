export interface ExplorePaper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  published: string;
  category: string;
  link: string;
  citation_count: number;
  concepts?: string[];
  // Deep analysis fields
  ai_analysis?: {
    impactScore?: number;
    difficultyLevel?: string;
    hasCode?: boolean;
    researchSignificance?: string;
    summary?: string;
    keyContribution?: string;
  };
  deep_analysis?: {
    impact_assessment?: {
      impact_score?: number;
    };
    reader_guidance?: {
      difficulty_level?: string;
      estimated_reading_time?: number;
    };
    technical_depth?: {
      reproducibility_score?: number;
    };
    novelty_assessment?: {
      novelty_type?: string;
    };
  };
  code_repos?: string[];
}

export interface ExploreFilters {
  hasCode: boolean;
  highImpact: boolean;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert" | null;
  category: string | null;
  sortBy: "recent" | "citations" | "impact";
}

export interface TrendingTopic {
  name: string;
  count: number;
  acceleration: number;
}

export interface AdvisorMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  papers?: Array<{
    id: string;
    title: string;
    summary: string;
  }>;
  suggestions?: string[];
  timestamp: Date;
}
