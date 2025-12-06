export interface TrendingTopic {
  name: string;
  normalized_name: string;
  category: string;
  current_count: number;
  previous_count: number;
  acceleration: number;
  representative_papers: Array<{
    id: string;
    title: string;
    published?: string;
  }>;
  related_topics: string[];
}

export interface RisingTechnique {
  name: string;
  normalized_name: string;
  category: string;
  current_count: number;
  previous_count: number;
  acceleration: number;
}

export interface ActiveAuthor {
  name: string;
  paper_count: number;
  recent_papers: number;
  top_topics: string[];
}

export interface TrendSummary {
  hot_topics: TrendingTopic[];
  rising_techniques: RisingTechnique[];
  active_authors: ActiveAuthor[];
  emerging_areas: string[];
  generated_at: string;
}

export interface TechniqueComparison {
  technique_a: {
    name: string;
    normalized_name: string;
    paper_count: number;
    representative_papers: Array<{ id: string; title: string }>;
    top_domains: Array<[string, number]>;
  };
  technique_b: {
    name: string;
    normalized_name: string;
    paper_count: number;
    representative_papers: Array<{ id: string; title: string }>;
    top_domains: Array<[string, number]>;
  };
  comparison: {
    window_days: number;
    count_ratio: number;
    common_domains: string[];
  };
}
