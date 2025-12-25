"use client";

import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

// Types
interface GitHubStats {
  total_stars: number;
  repo_count: number;
  top_repo?: {
    url: string;
    stars: number;
    forks: number;
    language?: string;
    pushed_at?: string;
    license?: string;
  };
}

interface DiscoveryStats {
  coverage: {
    total_papers: number;
    ai_analyzed: number;
    deep_analyzed: number;
    with_code: number;
  };
  distributions: {
    impact_scores: Record<string, number>;
    difficulty_levels: Record<string, number>;
    novelty_types: Record<string, number>;
    categories: Record<string, number>;
  };
}

interface ImpactPaper {
  id: string;
  title: string;
  published: string;
  category: string;
  impact_score: number;
  citation_potential?: string;
  industry_relevance?: string;
  executive_summary?: string;
  novelty_type?: string;
  github_stats?: GitHubStats;
  citation_count?: number;
  influential_citation_count?: number;
}

interface TLDRPaper {
  id: string;
  title: string;
  published: string;
  category: string;
  executive_summary?: string;
  problem_statement?: string;
  proposed_solution?: string;
  key_contribution?: string;
  reading_time_minutes?: number;
  github_stats?: GitHubStats;
}

interface RisingPaper {
  id: string;
  title: string;
  published: string;
  category: string;
  citation_count: number;
  citation_velocity: number;
  months_since_publication: number;
  link: string;
  github_stats?: GitHubStats;
}

interface TechniquePaper {
  id: string;
  title: string;
  novelty_type?: string;
  novelty_description?: string;
  methodology_approach?: string;
  key_components: string[];
  github_stats?: GitHubStats;
}

interface ReproduciblePaper {
  id: string;
  title: string;
  reproducibility_score?: number;
  code_availability?: string;
  github_urls: string[];
  datasets_mentioned: string[];
  has_code: boolean;
  github_stats?: GitHubStats;
}

interface HotTopic {
  name: string;
  paper_count: number;
  total_citations: number;
  avg_citation_velocity: number;
  velocity_tier: string;
  trend_direction: string;
  top_papers: Array<{ id: string; title: string; velocity: number; citations: number }>;
}

interface LearningPathPaper {
  id: string;
  title: string;
  difficulty_level: string;
  prerequisites: string[];
  reading_time_minutes: number;
  key_sections: string[];
  summary?: string;
}

interface LearningPathLevel {
  level: string;
  description: string;
  papers: LearningPathPaper[];
}

interface LearningPathData {
  topic: string | null;
  category: string | null;
  path: LearningPathLevel[];
}

type TabId = "overview" | "impact" | "tldr" | "rising" | "techniques" | "reproducible" | "hot-topics" | "learning-path";

const TABS: { id: TabId; label: string; icon: JSX.Element; description: string }[] = [
  {
    id: "overview",
    label: "Overview",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
    description: "Research insights at a glance",
  },
  {
    id: "impact",
    label: "High Impact",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
    description: "Papers with highest research impact",
  },
  {
    id: "tldr",
    label: "TL;DR",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
    description: "Quick summaries for fast scanning",
  },
  {
    id: "rising",
    label: "Rising",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
        <polyline points="17 6 23 6 23 12" />
      </svg>
    ),
    description: "Papers gaining citation momentum",
  },
  {
    id: "hot-topics",
    label: "Hot Topics",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2c1.4 0 2.7.4 3.8 1.1.2.1.3.3.3.5 0 .3-.2.5-.5.5-2.4-.1-4.6 1.1-5.8 3.1-1.2 2-1.3 4.4-.4 6.5.2.4.4.7.7 1 .1.1.2.3.2.5 0 .4-.4.6-.7.5C5.6 14.3 3.5 11 4.1 7.5 4.7 4.3 7.9 2 12 2z" />
        <path d="M15.5 8c.8.5 1.4 1.3 1.7 2.2.3.9.3 1.9-.1 2.8-.5 1.1-1.4 2-2.5 2.4-.2.1-.4.1-.6 0-.3-.1-.4-.4-.3-.7.3-.7.3-1.4.1-2.1-.2-.7-.7-1.3-1.3-1.7-.2-.1-.3-.4-.2-.6.1-.3.4-.4.6-.3 1.1.4 1.9 1.2 2.4 2.2" />
      </svg>
    ),
    description: "Trending research topics",
  },
  {
    id: "techniques",
    label: "Techniques",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l9 4.5v9L12 21l-9-4.5v-9L12 3z" />
        <path d="M12 12l9-4.5" />
        <path d="M12 12v9" />
        <path d="M12 12L3 7.5" />
      </svg>
    ),
    description: "Browse by methodology type",
  },
  {
    id: "reproducible",
    label: "Reproducible",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
      </svg>
    ),
    description: "Papers with code & high reproducibility",
  },
  {
    id: "learning-path",
    label: "Learning Path",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
      </svg>
    ),
    description: "Curated learning progression by difficulty",
  },
];

export default function DiscoveryPage() {
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as TabId | null;
  const validTabs: TabId[] = ["overview", "impact", "tldr", "rising", "techniques", "reproducible", "hot-topics", "learning-path"];
  const initialTab = tabParam && validTabs.includes(tabParam) ? tabParam : "overview";
  const [activeTab, setActiveTab] = useState<TabId>(initialTab);
  const [stats, setStats] = useState<DiscoveryStats | null>(null);
  const [impactPapers, setImpactPapers] = useState<ImpactPaper[]>([]);
  const [tldrPapers, setTldrPapers] = useState<TLDRPaper[]>([]);
  const [risingPapers, setRisingPapers] = useState<RisingPaper[]>([]);
  const [techniquePapers, setTechniquePapers] = useState<TechniquePaper[]>([]);
  const [reproduciblePapers, setReproduciblePapers] = useState<ReproduciblePaper[]>([]);
  const [hotTopics, setHotTopics] = useState<HotTopic[]>([]);
  const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noveltyFilter, setNoveltyFilter] = useState<string | null>(null);
  const [noveltyDistribution, setNoveltyDistribution] = useState<Record<string, number>>({});
  const [frameworkFilter, setFrameworkFilter] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [learningPathTopic, setLearningPathTopic] = useState<string>("");

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(API_BASE ? `${API_BASE}/discovery/stats` : "/api/discovery/stats");
      if (!response.ok) throw new Error("Failed to fetch stats");
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error("Error fetching stats:", err);
    }
  }, []);

  const fetchImpactPapers = useCallback(async () => {
    setLoading(true);
    try {
      const categoryParam = categoryFilter ? `&category=${categoryFilter}` : "";
      const response = await fetch(
        API_BASE ? `${API_BASE}/discovery/impact?min_score=7&limit=20${categoryParam}` : `/api/discovery/impact?min_score=7&limit=20${categoryParam}`
      );
      if (!response.ok) throw new Error("Failed to fetch impact papers");
      const data = await response.json();
      setImpactPapers(data.papers || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  const fetchTLDRPapers = useCallback(async () => {
    setLoading(true);
    try {
      const categoryParam = categoryFilter ? `&category=${categoryFilter}` : "";
      const response = await fetch(
        API_BASE ? `${API_BASE}/discovery/tldr?days=7&limit=20${categoryParam}` : `/api/discovery/tldr?days=7&limit=20${categoryParam}`
      );
      if (!response.ok) throw new Error("Failed to fetch TL;DR papers");
      const data = await response.json();
      setTldrPapers(data.papers || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  const fetchRisingPapers = useCallback(async () => {
    setLoading(true);
    try {
      const categoryParam = categoryFilter ? `&category=${categoryFilter}` : "";
      const response = await fetch(
        API_BASE ? `${API_BASE}/discovery/rising?min_citations=5&limit=20${categoryParam}` : `/api/discovery/rising?min_citations=5&limit=20${categoryParam}`
      );
      if (!response.ok) throw new Error("Failed to fetch rising papers");
      const data = await response.json();
      setRisingPapers(data.papers || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  const fetchTechniquePapers = useCallback(async () => {
    setLoading(true);
    try {
      const categoryParam = categoryFilter ? `&category=${categoryFilter}` : "";
      const noveltyParam = noveltyFilter ? `&novelty_type=${noveltyFilter}` : "";
      const url = `${API_BASE}/discovery/techniques?limit=20${noveltyParam}${categoryParam}`;
      const response = await fetch(API_BASE ? url : url.replace(API_BASE, "/api"));
      if (!response.ok) throw new Error("Failed to fetch technique papers");
      const data = await response.json();
      setTechniquePapers(data.papers || []);
      setNoveltyDistribution(data.novelty_type_distribution || {});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [noveltyFilter, categoryFilter]);

  const fetchReproduciblePapers = useCallback(async () => {
    setLoading(true);
    try {
      const categoryParam = categoryFilter ? `&category=${categoryFilter}` : "";
      const response = await fetch(
        API_BASE
          ? `${API_BASE}/discovery/reproducible?min_reproducibility=7&has_code=true&limit=20${categoryParam}`
          : `/api/discovery/reproducible?min_reproducibility=7&has_code=true&limit=20${categoryParam}`
      );
      if (!response.ok) throw new Error("Failed to fetch reproducible papers");
      const data = await response.json();
      setReproduciblePapers(data.papers || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  const fetchHotTopics = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(
        API_BASE ? `${API_BASE}/discovery/hot-topics?days=30&limit=15` : "/api/discovery/hot-topics?days=30&limit=15"
      );
      if (!response.ok) throw new Error("Failed to fetch hot topics");
      const data = await response.json();
      setHotTopics(data.topics || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLearningPath = useCallback(async (topic?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "20" });
      if (topic && topic.trim()) {
        params.set("topic", topic.trim());
      }
      const url = API_BASE
        ? `${API_BASE}/discovery/learning-path?${params.toString()}`
        : `/api/discovery/learning-path?${params.toString()}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch learning path");
      const data = await response.json();
      setLearningPath(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch data based on active tab
  useEffect(() => {
    setError(null);
    switch (activeTab) {
      case "overview":
        fetchStats();
        fetchImpactPapers();
        break;
      case "impact":
        fetchImpactPapers();
        break;
      case "tldr":
        fetchTLDRPapers();
        break;
      case "rising":
        fetchRisingPapers();
        break;
      case "techniques":
        fetchTechniquePapers();
        break;
      case "reproducible":
        fetchReproduciblePapers();
        break;
      case "hot-topics":
        fetchHotTopics();
        break;
      case "learning-path":
        fetchLearningPath(learningPathTopic);
        break;
    }
  }, [activeTab, fetchStats, fetchImpactPapers, fetchTLDRPapers, fetchRisingPapers, fetchTechniquePapers, fetchReproduciblePapers, fetchHotTopics, fetchLearningPath, learningPathTopic]);

  const formatDate = (dateStr: string | null | undefined): string => {
    if (!dateStr) return "Unknown date";
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return "Unknown date";
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  const getVelocityTierColor = (tier: string) => {
    switch (tier) {
      case "viral": return "discovery-badge--viral";
      case "hot": return "discovery-badge--hot";
      case "rising": return "discovery-badge--rising";
      case "growing": return "discovery-badge--growing";
      default: return "discovery-badge--emerging";
    }
  };

  const getTrendIcon = (direction: string) => {
    if (direction === "up") return "↑";
    if (direction === "down") return "↓";
    return "→";
  };

  const formatStars = (stars: number): string => {
    if (stars >= 1000) {
      return `${(stars / 1000).toFixed(1)}k`;
    }
    return stars.toString();
  };

  const formatRelativeTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "today";
    if (diffDays === 1) return "yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  };

  const isRecentlyUpdated = (dateStr: string): boolean => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays < 90;
  };

  const detectFrameworks = (text?: string, components?: string[]): string[] => {
    if (!text && (!components || components.length === 0)) return [];

    const frameworks: Set<string> = new Set();
    const searchText = `${text || ""} ${components?.join(" ") || ""}`.toLowerCase();

    // Framework patterns (case-insensitive)
    const patterns = [
      { name: "PyTorch", regex: /\bpytorch\b|\btorch\b(?!\.js)/ },
      { name: "TensorFlow", regex: /\btensorflow\b|\btf\b/ },
      { name: "JAX", regex: /\bjax\b|\bflax\b/ },
      { name: "Keras", regex: /\bkeras\b/ },
      { name: "Hugging Face", regex: /\bhugging\s*face\b|\btransformers\b(?=\slibrary|\sframework)/ },
      { name: "scikit-learn", regex: /\bscikit[-\s]learn\b|\bsklearn\b/ },
      { name: "MXNet", regex: /\bmxnet\b/ },
      { name: "PaddlePaddle", regex: /\bpaddlepaddle\b|\bpaddle\b/ }
    ];

    for (const { name, regex } of patterns) {
      if (regex.test(searchText)) {
        frameworks.add(name);
      }
    }

    return Array.from(frameworks);
  };

  const renderFrameworkBadges = (frameworks: string[]) => {
    if (frameworks.length === 0) return null;

    return frameworks.slice(0, 3).map((framework) => (
      <span key={framework} className="discovery-framework-badge" title={`Uses ${framework}`}>
        {framework}
      </span>
    ));
  };

  const isProductionReady = (paper: {
    has_code?: boolean;
    reproducibility_score?: number;
    github_stats?: GitHubStats;
  }): boolean => {
    // Production ready criteria (all must be met):
    // 1. Has code available
    if (!paper.has_code) return false;

    // 2. High reproducibility (7+/10)
    if (!paper.reproducibility_score || paper.reproducibility_score < 7) return false;

    // 3. GitHub repo with community adoption (50+ stars) OR active maintenance
    if (paper.github_stats) {
      const stars = paper.github_stats.total_stars || 0;
      const pushedAt = paper.github_stats.top_repo?.pushed_at;
      const recentlyUpdated = pushedAt && isRecentlyUpdated(pushedAt);

      // Either has good community adoption OR is actively maintained
      if (stars >= 50 || recentlyUpdated) {
        return true;
      }
    }

    return false;
  };

  const renderProductionReadyBadge = (paper: {
    has_code?: boolean;
    reproducibility_score?: number;
    github_stats?: GitHubStats;
  }) => {
    if (!isProductionReady(paper)) return null;

    return (
      <span
        className="discovery-production-badge"
        title="Production Ready: High reproducibility (7+), active code repository, and community adoption"
      >
        ✓ Production Ready
      </span>
    );
  };

  const renderGitHubIndicator = (github_stats?: GitHubStats) => {
    if (!github_stats || github_stats.total_stars === 0) return null;
    const topRepo = github_stats.top_repo;
    const isActive = topRepo?.pushed_at && isRecentlyUpdated(topRepo.pushed_at);
    const license = topRepo?.license;

    return (
      <a
        href={topRepo?.url || "#"}
        target="_blank"
        rel="noopener noreferrer"
        className={`discovery-github-indicator ${isActive ? "discovery-github-indicator--active" : ""}`}
        title={`${github_stats.total_stars} stars${topRepo?.language ? ` • ${topRepo.language}` : ""}${license ? ` • ${license} license` : ""}${topRepo?.pushed_at ? ` • Updated ${formatRelativeTime(topRepo.pushed_at)}` : ""}`}
        onClick={(e) => e.stopPropagation()}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
        </svg>
        <span className="discovery-github-indicator__stars">{formatStars(github_stats.total_stars)}</span>
        {isActive && <span className="discovery-github-indicator__active" title="Recently updated" />}
        {license && <span className="discovery-license-badge" title={`${license} license`}>{license}</span>}
      </a>
    );
  };

  const formatCitations = (count: number): string => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  const renderCitationIndicator = (citation_count?: number, influential_citation_count?: number) => {
    if (!citation_count || citation_count === 0) return null;
    const influentialPct = influential_citation_count && citation_count > 0
      ? Math.round((influential_citation_count / citation_count) * 100)
      : 0;
    const isHighlyInfluential = influentialPct >= 30;

    return (
      <span
        className={`discovery-citation-indicator ${isHighlyInfluential ? "discovery-citation-indicator--influential" : ""}`}
        title={`${citation_count} citations${influential_citation_count ? ` (${influential_citation_count} influential, ${influentialPct}%)` : ""}`}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 7 7 7 7" />
          <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 17 7 17 7" />
          <path d="M4 22h16" />
          <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
          <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
          <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
        </svg>
        <span className="discovery-citation-indicator__count">{formatCitations(citation_count)}</span>
        {isHighlyInfluential && <span className="discovery-citation-indicator__influential" title="High-quality citations" />}
      </span>
    );
  };

  return (
    <main className="discovery-page">
      {/* Header */}
      <header className="discovery-header">
        <div className="discovery-header__content">
          <h1 className="discovery-header__title">Discovery</h1>
          <p className="discovery-header__subtitle">
            AI-powered paper recommendations based on impact, trends, and your research interests
          </p>
        </div>
        <Link href="/explore" className="btn btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          Search Papers
        </Link>
      </header>

      {/* Tab Navigation */}
      <nav className="discovery-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`discovery-tab ${activeTab === tab.id ? "discovery-tab--active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon}
            <span className="discovery-tab__label">{tab.label}</span>
          </button>
        ))}
      </nav>

      {/* Tab Description */}
      <div className="discovery-tab-description">
        {TABS.find((t) => t.id === activeTab)?.description}
      </div>

      {/* Category Filter Bar */}
      {activeTab !== "overview" && activeTab !== "hot-topics" && activeTab !== "learning-path" && stats?.distributions.categories && (
        <div className="discovery-category-filter">
          <span className="discovery-category-filter__label">Filter by Category:</span>
          <div className="discovery-category-filter__buttons">
            <button
              className={`discovery-filter-btn ${categoryFilter === null ? "discovery-filter-btn--active" : ""}`}
              onClick={() => setCategoryFilter(null)}
            >
              All
            </button>
            {Object.entries(stats.distributions.categories).slice(0, 8).map(([cat, count]) => (
              <button
                key={cat}
                className={`discovery-filter-btn ${categoryFilter === cat ? "discovery-filter-btn--active" : ""}`}
                onClick={() => setCategoryFilter(cat)}
              >
                {cat} ({(count as number).toLocaleString()})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="discovery-error">
          <p>Error: {error}</p>
          <button className="btn btn-secondary" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {/* Content */}
      <div className="discovery-content">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="discovery-overview">
            {/* Stats Cards */}
            {stats && (
              <div className="discovery-stats">
                <div className="discovery-stat-card">
                  <div className="discovery-stat-card__value">
                    {stats.coverage.total_papers.toLocaleString()}
                  </div>
                  <div className="discovery-stat-card__label">Total Papers</div>
                </div>
                <div className="discovery-stat-card">
                  <div className="discovery-stat-card__value">
                    {stats.coverage.deep_analyzed.toLocaleString()}
                  </div>
                  <div className="discovery-stat-card__label">Deep Analyzed</div>
                </div>
                <div className="discovery-stat-card">
                  <div className="discovery-stat-card__value">
                    {stats.coverage.with_code.toLocaleString()}
                  </div>
                  <div className="discovery-stat-card__label">With Code</div>
                </div>
                <div className="discovery-stat-card discovery-stat-card--highlight">
                  <div className="discovery-stat-card__value">
                    {Math.round((stats.coverage.deep_analyzed / stats.coverage.total_papers) * 100)}%
                  </div>
                  <div className="discovery-stat-card__label">Enrichment Coverage</div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="discovery-quick-actions">
              <h2 className="discovery-section-title">Quick Discovery</h2>
              <div className="discovery-action-cards">
                <button className="discovery-action-card" onClick={() => setActiveTab("impact")}>
                  <span className="discovery-action-card__icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                  </span>
                  <span className="discovery-action-card__title">High Impact Papers</span>
                  <span className="discovery-action-card__desc">Top-rated research breakthroughs</span>
                </button>
                <button className="discovery-action-card" onClick={() => setActiveTab("rising")}>
                  <span className="discovery-action-card__icon discovery-action-card__icon--rising">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                      <polyline points="17 6 23 6 23 12" />
                    </svg>
                  </span>
                  <span className="discovery-action-card__title">Rising Stars</span>
                  <span className="discovery-action-card__desc">Gaining citations fast</span>
                </button>
                <button className="discovery-action-card" onClick={() => setActiveTab("reproducible")}>
                  <span className="discovery-action-card__icon discovery-action-card__icon--code">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
                    </svg>
                  </span>
                  <span className="discovery-action-card__title">Papers with Code</span>
                  <span className="discovery-action-card__desc">Ready to reproduce</span>
                </button>
                <button className="discovery-action-card" onClick={() => setActiveTab("tldr")}>
                  <span className="discovery-action-card__icon discovery-action-card__icon--tldr">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                  </span>
                  <span className="discovery-action-card__title">TL;DR Feed</span>
                  <span className="discovery-action-card__desc">Quick paper summaries</span>
                </button>
              </div>
            </div>

            {/* Recent High Impact */}
            <div className="discovery-section">
              <h2 className="discovery-section-title">Recent High Impact Papers</h2>
              {loading ? (
                <div className="discovery-loading">
                  <div className="spinner" />
                  <span>Loading papers...</span>
                </div>
              ) : (
                <div className="discovery-paper-grid">
                  {impactPapers.slice(0, 6).map((paper) => (
                    <article key={paper.id} className="discovery-paper-card">
                      <div className="discovery-paper-card__badges">
                        <span className="discovery-badge discovery-badge--impact">
                          Impact: {paper.impact_score}/10
                        </span>
                        {paper.novelty_type && (
                          <span className="discovery-badge">{paper.novelty_type}</span>
                        )}
                      </div>
                      <h3 className="discovery-paper-card__title">
                        <a href={`https://arxiv.org/abs/${paper.id}`} target="_blank" rel="noopener noreferrer">
                          {paper.title}
                        </a>
                      </h3>
                      {paper.executive_summary && (
                        <p className="discovery-paper-card__summary">{paper.executive_summary}</p>
                      )}
                      <div className="discovery-paper-card__meta">
                        <span>{formatDate(paper.published)}</span>
                        <span>{paper.category}</span>
                        {renderCitationIndicator(paper.citation_count, paper.influential_citation_count)}
                        {renderGitHubIndicator(paper.github_stats)}
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Impact Tab */}
        {activeTab === "impact" && (
          <div className="discovery-list">
            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Loading high impact papers...</span>
              </div>
            ) : (
              impactPapers.map((paper) => (
                <article key={paper.id} className="discovery-paper-row">
                  <div className="discovery-paper-row__score">
                    <span className="discovery-impact-score">{paper.impact_score}</span>
                    <span className="discovery-impact-label">Impact</span>
                  </div>
                  <div className="discovery-paper-row__content">
                    <h3 className="discovery-paper-row__title">
                      <a href={`https://arxiv.org/abs/${paper.id}`} target="_blank" rel="noopener noreferrer">
                        {paper.title}
                      </a>
                    </h3>
                    {paper.executive_summary && (
                      <p className="discovery-paper-row__summary">{paper.executive_summary}</p>
                    )}
                    <div className="discovery-paper-row__meta">
                      <span>{formatDate(paper.published)}</span>
                      <span>{paper.category}</span>
                      {paper.industry_relevance && (
                        <span className="discovery-badge discovery-badge--small">
                          Industry: {paper.industry_relevance}
                        </span>
                      )}
                      {paper.novelty_type && (
                        <span className="discovery-badge discovery-badge--small">{paper.novelty_type}</span>
                      )}
                      {renderCitationIndicator(paper.citation_count, paper.influential_citation_count)}
                      {renderGitHubIndicator(paper.github_stats)}
                    </div>
                  </div>
                  <div className="discovery-paper-row__actions">
                    <Link href={`/explore?paper=${paper.id}`} className="btn btn-secondary btn-sm">
                      View Details
                    </Link>
                  </div>
                </article>
              ))
            )}
          </div>
        )}

        {/* TL;DR Tab */}
        {activeTab === "tldr" && (
          <div className="discovery-tldr-grid">
            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Loading summaries...</span>
              </div>
            ) : tldrPapers.length === 0 ? (
              <div className="discovery-empty-state">
                <p>No recent papers with executive summaries found from the last 7 days.</p>
                <p className="discovery-empty-state__hint">
                  Papers typically get summaries after deep analysis. Try adjusting the time range or check back later.
                </p>
              </div>
            ) : (
              tldrPapers.map((paper) => (
                <article key={paper.id} className="discovery-tldr-card">
                  <div className="discovery-tldr-card__header">
                    <span className="discovery-badge">{paper.category}</span>
                    {paper.reading_time_minutes && (
                      <span className="discovery-tldr-card__time">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <polyline points="12 6 12 12 16 14" />
                        </svg>
                        {paper.reading_time_minutes} min read
                      </span>
                    )}
                    {renderGitHubIndicator(paper.github_stats)}
                  </div>
                  <h3 className="discovery-tldr-card__title">
                    <a href={`https://arxiv.org/abs/${paper.id}`} target="_blank" rel="noopener noreferrer">
                      {paper.title}
                    </a>
                  </h3>
                  {paper.executive_summary && (
                    <div className="discovery-tldr-card__section">
                      <strong>TL;DR:</strong> {paper.executive_summary}
                    </div>
                  )}
                  {paper.problem_statement && (
                    <div className="discovery-tldr-card__section">
                      <strong>Problem:</strong> {paper.problem_statement}
                    </div>
                  )}
                  {paper.proposed_solution && (
                    <div className="discovery-tldr-card__section">
                      <strong>Solution:</strong> {paper.proposed_solution}
                    </div>
                  )}
                  <div className="discovery-tldr-card__footer">
                    <span>{formatDate(paper.published)}</span>
                    <a
                      href={`https://arxiv.org/abs/${paper.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="discovery-tldr-card__link"
                    >
                      Read Full Paper →
                    </a>
                  </div>
                </article>
              ))
            )}
          </div>
        )}

        {/* Rising Tab */}
        {activeTab === "rising" && (
          <div className="discovery-list">
            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Finding rising papers...</span>
              </div>
            ) : (
              risingPapers.map((paper) => (
                <article key={paper.id} className="discovery-paper-row discovery-paper-row--rising">
                  <div className="discovery-paper-row__velocity">
                    <span className="discovery-velocity-value">{paper.citation_velocity.toFixed(1)}</span>
                    <span className="discovery-velocity-label">cites/mo</span>
                  </div>
                  <div className="discovery-paper-row__content">
                    <h3 className="discovery-paper-row__title">
                      <a href={paper.link} target="_blank" rel="noopener noreferrer">
                        {paper.title}
                      </a>
                    </h3>
                    <div className="discovery-paper-row__meta">
                      <span>{paper.citation_count} total citations</span>
                      <span>{paper.months_since_publication.toFixed(1)} months old</span>
                      <span>{paper.category}</span>
                      {renderGitHubIndicator(paper.github_stats)}
                    </div>
                  </div>
                  <div className="discovery-paper-row__trend">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                      <polyline points="17 6 23 6 23 12" />
                    </svg>
                  </div>
                </article>
              ))
            )}
          </div>
        )}

        {/* Hot Topics Tab */}
        {activeTab === "hot-topics" && (
          <div className="discovery-topics-grid">
            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Finding trending topics...</span>
              </div>
            ) : (
              hotTopics.map((topic, index) => (
                <article key={topic.name} className="discovery-topic-card">
                  <div className="discovery-topic-card__header">
                    <span className="discovery-topic-card__rank">#{index + 1}</span>
                    <span className={`discovery-badge ${getVelocityTierColor(topic.velocity_tier)}`}>
                      {topic.velocity_tier}
                    </span>
                    <span className="discovery-topic-card__trend">
                      {getTrendIcon(topic.trend_direction)}
                    </span>
                  </div>
                  <h3 className="discovery-topic-card__name">{topic.name}</h3>
                  <div className="discovery-topic-card__stats">
                    <div className="discovery-topic-stat">
                      <span className="discovery-topic-stat__value">{topic.paper_count}</span>
                      <span className="discovery-topic-stat__label">papers</span>
                    </div>
                    <div className="discovery-topic-stat">
                      <span className="discovery-topic-stat__value">{topic.total_citations}</span>
                      <span className="discovery-topic-stat__label">citations</span>
                    </div>
                    <div className="discovery-topic-stat">
                      <span className="discovery-topic-stat__value">{topic.avg_citation_velocity.toFixed(1)}</span>
                      <span className="discovery-topic-stat__label">avg velocity</span>
                    </div>
                  </div>
                  {topic.top_papers && topic.top_papers.length > 0 && (
                    <div className="discovery-topic-card__papers">
                      <h4>Top Papers:</h4>
                      <ul>
                        {topic.top_papers.slice(0, 3).map((p, i) => (
                          <li key={i}>
                            <a href={`https://arxiv.org/abs/${p.id}`} target="_blank" rel="noopener noreferrer">
                              {p.title.length > 60 ? p.title.slice(0, 60) + "..." : p.title}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </article>
              ))
            )}
          </div>
        )}

        {/* Techniques Tab */}
        {activeTab === "techniques" && (() => {
          // Compute framework distribution from all papers
          const frameworkCounts: Record<string, number> = {};
          const papersWithFrameworks = techniquePapers.map((paper) => {
            const frameworks = detectFrameworks(paper.methodology_approach, paper.key_components);
            frameworks.forEach((fw) => {
              frameworkCounts[fw] = (frameworkCounts[fw] || 0) + 1;
            });
            return { ...paper, frameworks };
          });

          // Filter papers by framework
          const filteredPapers = frameworkFilter
            ? papersWithFrameworks.filter((p) => p.frameworks.includes(frameworkFilter))
            : papersWithFrameworks;

          return (
            <div className="discovery-techniques">
              <div className="discovery-techniques__filters">
                <div className="discovery-techniques__filters-row">
                  <span className="discovery-techniques__filters-label">Novelty:</span>
                  <button
                    className={`discovery-filter-btn ${noveltyFilter === null ? "discovery-filter-btn--active" : ""}`}
                    onClick={() => setNoveltyFilter(null)}
                  >
                    All
                  </button>
                  {Object.entries(noveltyDistribution).slice(0, 5).map(([type, count]) => (
                    <button
                      key={type}
                      className={`discovery-filter-btn ${noveltyFilter === type ? "discovery-filter-btn--active" : ""}`}
                      onClick={() => setNoveltyFilter(type)}
                    >
                      {type} ({count})
                    </button>
                  ))}
                </div>
                {Object.keys(frameworkCounts).length > 0 && (
                  <div className="discovery-techniques__filters-row">
                    <span className="discovery-techniques__filters-label">Framework:</span>
                    <button
                      className={`discovery-filter-btn ${frameworkFilter === null ? "discovery-filter-btn--active" : ""}`}
                      onClick={() => setFrameworkFilter(null)}
                    >
                      All
                    </button>
                    {Object.entries(frameworkCounts)
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 6)
                      .map(([framework, count]) => (
                        <button
                          key={framework}
                          className={`discovery-filter-btn discovery-filter-btn--framework ${frameworkFilter === framework ? "discovery-filter-btn--active" : ""}`}
                          onClick={() => setFrameworkFilter(framework)}
                        >
                          {framework} ({count})
                        </button>
                      ))}
                  </div>
                )}
              </div>
              <div className="discovery-list">
                {loading ? (
                  <div className="discovery-loading">
                    <div className="spinner" />
                    <span>Loading techniques...</span>
                  </div>
                ) : (
                  filteredPapers.map((paper) => (
                    <article key={paper.id} className="discovery-technique-card">
                      <div className="discovery-technique-card__header">
                        {paper.novelty_type && (
                          <span className="discovery-badge discovery-badge--technique">{paper.novelty_type}</span>
                        )}
                        {renderFrameworkBadges(paper.frameworks)}
                        {renderGitHubIndicator(paper.github_stats)}
                      </div>
                    <h3 className="discovery-technique-card__title">
                      <a href={`https://arxiv.org/abs/${paper.id}`} target="_blank" rel="noopener noreferrer">
                        {paper.title}
                      </a>
                    </h3>
                    {paper.novelty_description && (
                      <p className="discovery-technique-card__description">{paper.novelty_description}</p>
                    )}
                    {paper.methodology_approach && (
                      <div className="discovery-technique-card__approach">
                        <strong>Approach:</strong> {paper.methodology_approach}
                      </div>
                    )}
                    {paper.key_components && paper.key_components.length > 0 && (
                      <div className="discovery-technique-card__components">
                        {paper.key_components.map((comp, i) => (
                          <span key={i} className="discovery-technique-chip">{comp}</span>
                        ))}
                      </div>
                    )}
                  </article>
                  ))
                )}
              </div>
            </div>
          );
        })()}

        {/* Reproducible Tab */}
        {activeTab === "reproducible" && (
          <div className="discovery-list">
            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Finding reproducible papers...</span>
              </div>
            ) : (
              reproduciblePapers.map((paper) => (
                <article key={paper.id} className="discovery-paper-row discovery-paper-row--reproducible">
                  <div className="discovery-paper-row__score">
                    <span className="discovery-repro-score">{paper.reproducibility_score || "N/A"}</span>
                    <span className="discovery-repro-label">Repro</span>
                  </div>
                  <div className="discovery-paper-row__content">
                    <h3 className="discovery-paper-row__title">
                      <a href={`https://arxiv.org/abs/${paper.id}`} target="_blank" rel="noopener noreferrer">
                        {paper.title}
                      </a>
                    </h3>
                    <div className="discovery-paper-row__meta">
                      {renderProductionReadyBadge(paper)}
                      {paper.code_availability && (
                        <span className="discovery-badge discovery-badge--code">{paper.code_availability}</span>
                      )}
                      {renderGitHubIndicator(paper.github_stats)}
                      {!paper.github_stats && paper.github_urls && paper.github_urls.length > 0 && (
                        <a
                          href={paper.github_urls[0]}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="discovery-github-link"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                          </svg>
                          View Code
                        </a>
                      )}
                    </div>
                    {paper.datasets_mentioned && paper.datasets_mentioned.length > 0 && (
                      <div className="discovery-paper-row__datasets">
                        <span className="discovery-datasets-label">Datasets:</span>
                        {paper.datasets_mentioned.slice(0, 5).map((ds, i) => (
                          <span key={i} className="discovery-dataset-chip">{ds}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </article>
              ))
            )}
          </div>
        )}

        {/* Learning Path Tab */}
        {activeTab === "learning-path" && (
          <div className="discovery-learning-path">
            {/* Topic Search */}
            <div className="discovery-learning-path__search">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  fetchLearningPath(learningPathTopic);
                }}
                className="discovery-learning-path__form"
              >
                <input
                  type="text"
                  placeholder="Enter a topic (e.g., transformers, diffusion models)..."
                  value={learningPathTopic}
                  onChange={(e) => setLearningPathTopic(e.target.value)}
                  className="discovery-learning-path__input"
                />
                <button type="submit" className="btn btn-primary">
                  Generate Path
                </button>
              </form>
              {learningPath?.topic && (
                <p className="discovery-learning-path__current">
                  Showing learning path for: <strong>{learningPath.topic}</strong>
                </p>
              )}
            </div>

            {loading ? (
              <div className="discovery-loading">
                <div className="spinner" />
                <span>Building your learning path...</span>
              </div>
            ) : learningPath?.path && learningPath.path.length > 0 ? (
              <div className="discovery-learning-path__levels">
                {learningPath.path.map((level, levelIndex) => (
                  <div key={level.level} className="discovery-learning-level">
                    <div className="discovery-learning-level__header">
                      <span className="discovery-learning-level__badge" data-level={level.level}>
                        {levelIndex + 1}. {level.level.charAt(0).toUpperCase() + level.level.slice(1)}
                      </span>
                      <span className="discovery-learning-level__desc">{level.description}</span>
                    </div>
                    <div className="discovery-learning-level__papers">
                      {level.papers.map((paper, paperIndex) => (
                        <article key={paper.id} className="discovery-learning-paper">
                          <div className="discovery-learning-paper__order">
                            {levelIndex + 1}.{paperIndex + 1}
                          </div>
                          <div className="discovery-learning-paper__content">
                            <h4 className="discovery-learning-paper__title">
                              <a
                                href={`https://arxiv.org/abs/${paper.id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {paper.title}
                              </a>
                            </h4>
                            {paper.summary && (
                              <p className="discovery-learning-paper__summary">{paper.summary}</p>
                            )}
                            <div className="discovery-learning-paper__meta">
                              {paper.reading_time_minutes > 0 && (
                                <span className="discovery-learning-paper__time">
                                  <svg
                                    width="12"
                                    height="12"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                  >
                                    <circle cx="12" cy="12" r="10" />
                                    <polyline points="12 6 12 12 16 14" />
                                  </svg>
                                  {paper.reading_time_minutes} min
                                </span>
                              )}
                              {paper.prerequisites && paper.prerequisites.length > 0 && (
                                <span className="discovery-learning-paper__prereqs">
                                  Prerequisites: {paper.prerequisites.join(", ")}
                                </span>
                              )}
                            </div>
                            {paper.key_sections && paper.key_sections.length > 0 && (
                              <div className="discovery-learning-paper__sections">
                                <span>Key sections:</span>
                                {paper.key_sections.map((section, i) => (
                                  <span key={i} className="discovery-technique-chip">
                                    {section}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </article>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="discovery-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
                <h3>Build Your Learning Path</h3>
                <p>
                  Enter a topic above to generate a curated progression of papers from beginner to
                  expert level.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
