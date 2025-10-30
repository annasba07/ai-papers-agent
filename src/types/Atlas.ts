export interface AtlasSummary {
  stats: {
    input_files: number;
    unique_papers: number;
    categories: string[];
    output_catalog: string;
    output_timeline: string;
    output_authors: string;
  };
  topCategories: Array<{ category: string; total: number }>;
  topAuthors: Array<{ author: string; paper_count: number }>;
}

export interface AtlasPaper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  published: string;
  category: string;
  link?: string;
  window_start?: string;
  window_end?: string;
}
