export interface GitHubRepoStats {
  url: string;
  owner: string;
  repo: string;
  stars: number;
  forks: number;
  open_issues?: number;
  language?: string;
  license?: string;
  pushed_at?: string;
  is_archived?: boolean;
  contributors?: number;
  topics?: string[];
}

export interface GitHubSignals {
  repos: GitHubRepoStats[];
  total_stars: number;
  updated_at?: string;
}

export interface ExternalSignals {
  github?: GitHubSignals;
}

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
  // GitHub enrichment data
  external_signals?: ExternalSignals;
}

export interface ExploreFilters {
  hasCode: boolean;
  highImpact: boolean;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert" | null;
  category: string | null;
  sortBy: "recent" | "citations" | "impact";
  timeRange: number | null; // Days - null means all time
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
