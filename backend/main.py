from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import requests
import xmltodict
import os
from dotenv import load_dotenv
import json
import asyncio
import redis
import hashlib
from google.generativeai import GenerativeModel, configure

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    # Add your Render frontend URL here when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # Required for SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"
    id = Column(String, primary_key=True, index=True) # arXiv ID
    title = Column(String, index=True)
    authors = Column(JSON) # Store as JSON array
    published = Column(DateTime)
    original_summary = Column(Text)
    ai_summary_json = Column(JSON) # Store AI summary as JSON object
    category = Column(String, index=True)
    link = Column(String) # Add link column
    fetched_at = Column(DateTime, default=datetime.utcnow)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"DEBUG: GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

configure(api_key=GEMINI_API_KEY)

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    print("Redis connected successfully")
except redis.ConnectionError:
    print("Redis not available, caching disabled")
    redis_client = None

def get_cache_key(title: str, abstract: str, analysis_type: str = "full") -> str:
    """Generate a consistent cache key for paper analysis"""
    content = f"{title}|{abstract}|{analysis_type}"
    return f"paper_analysis:{hashlib.md5(content.encode()).hexdigest()}"

def get_cached_analysis(title: str, abstract: str, analysis_type: str = "full") -> dict:
    """Retrieve cached analysis result"""
    if not redis_client:
        return None
    
    try:
        cache_key = get_cache_key(title, abstract, analysis_type)
        cached_result = redis_client.get(cache_key)
        if cached_result:
            print(f"Cache HIT for {analysis_type} analysis: {title[:50]}...")
            return json.loads(cached_result)
        else:
            print(f"Cache MISS for {analysis_type} analysis: {title[:50]}...")
            return None
    except Exception as e:
        print(f"Cache retrieval error: {e}")
        return None

def cache_analysis(title: str, abstract: str, result: dict, analysis_type: str = "full", ttl: int = 86400) -> None:
    """Cache analysis result with TTL (default 24 hours)"""
    if not redis_client:
        return
    
    try:
        cache_key = get_cache_key(title, abstract, analysis_type)
        redis_client.setex(cache_key, ttl, json.dumps(result))
        print(f"Cached {analysis_type} analysis: {title[:50]}...")
    except Exception as e:
        print(f"Cache storage error: {e}")

async def generate_technical_analysis(abstract: str, title: str) -> dict:
    """Stage 1: Deep technical analysis using Gemini Pro"""
    # Check cache first
    cached_result = get_cached_analysis(title, abstract, "technical")
    if cached_result:
        return cached_result
    
    try:
        model = GenerativeModel("gemini-1.5-flash")
        json_structure = '''
{
  "technicalInnovation": "Detailed explanation of the core technical mechanism or approach.",
  "methodologyBreakdown": "Step-by-step breakdown of how the proposed method works.",
  "performanceHighlights": "Key performance results and what makes them significant.",
  "implementationInsights": "Practical insights about implementation complexity and requirements.",
  "limitations": "Key limitations or potential issues with the approach.",
  "reproductionDifficulty": "low"
}
'''
        prompt = (
            "You are a technical AI expert analyzing the core innovation of this research paper. "
            "Focus ONLY on the technical depth and implementation reality.\n\n"
            "Title: {}\n\nAbstract: {}\n\n"
            "Provide detailed technical analysis:\n\n"
            "CORE TECHNICAL INNOVATION:\n"
            "- What specific technical mechanism is introduced?\n"
            "- How does the algorithm/architecture work step-by-step?\n"
            "- What are the key mathematical or computational insights?\n\n"
            "METHODOLOGY BREAKDOWN:\n"
            "- Break down the approach into clear, implementable steps\n"
            "- Explain key design decisions and why they matter\n"
            "- Identify algorithmic complexity and computational requirements\n\n"
            "PERFORMANCE ANALYSIS:\n"
            "- What are the key quantitative results?\n"
            "- Why are these results technically significant?\n"
            "- How do they compare to theoretical limits or previous work?\n\n"
            "IMPLEMENTATION REALITY:\n"
            "- What would it actually take to implement this?\n"
            "- What are the hardware/software requirements?\n"
            "- What are likely technical challenges or implementation gotchas?\n\n"
            "LIMITATIONS & REPRODUCTION:\n"
            "- What are the technical limitations or failure modes?\n"
            "- How difficult would this be to reproduce accurately?\n\n"
            "Return JSON: {}"
        ).format(title, abstract, json_structure)
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        # Cache the result
        cache_analysis(title, abstract, result, "technical")
        return result
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return {
            "technicalInnovation": "Technical analysis unavailable due to processing error.",
            "methodologyBreakdown": "Methodology analysis unavailable due to processing error.",
            "performanceHighlights": "Performance analysis unavailable due to processing error.",
            "implementationInsights": "Implementation analysis unavailable due to processing error.",
            "limitations": "Limitations analysis unavailable due to processing error.",
            "reproductionDifficulty": "medium"
        }

async def generate_research_context(abstract: str, title: str) -> dict:
    """Stage 2: Research positioning and context analysis"""
    # Check cache first
    cached_result = get_cached_analysis(title, abstract, "context")
    if cached_result:
        return cached_result
    
    try:
        model = GenerativeModel("gemini-1.5-flash")
        json_structure = '''
{
  "researchContext": "How this work relates to and builds upon existing research.",
  "futureImplications": "What this enables for future research or applications.",
  "researchSignificance": "breakthrough",
  "impactScore": 4.2
}
'''
        prompt = (
            "You are a research strategy expert analyzing how this paper fits in the broader research landscape. "
            "Focus on positioning, significance, and future implications.\n\n"
            "Title: {}\n\nAbstract: {}\n\n"
            "Provide research context analysis:\n\n"
            "RESEARCH POSITIONING:\n"
            "- How does this build on existing work in the field?\n"
            "- What research trajectory does this represent?\n"
            "- How does this differ from or improve upon recent approaches?\n\n"
            "FUTURE IMPLICATIONS:\n"
            "- What new research directions does this enable?\n"
            "- What practical applications become possible?\n"
            "- How might this influence the field's development?\n\n"
            "SIGNIFICANCE ASSESSMENT:\n"
            "- Is this incremental improvement, significant advance, or breakthrough?\n"
            "- What makes this work important (or not) for the field?\n"
            "- Rate impact potential on 1-5 scale based on novelty and significance\n\n"
            "Return JSON: {}"
        ).format(title, abstract, json_structure)
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        # Cache the result
        cache_analysis(title, abstract, result, "context")
        return result
    except Exception as e:
        print(f"Error in research context analysis: {e}")
        return {
            "researchContext": "Research context analysis unavailable due to processing error.",
            "futureImplications": "Future implications analysis unavailable due to processing error.",
            "researchSignificance": "incremental",
            "impactScore": 3.0
        }

async def generate_practical_assessment(abstract: str, title: str) -> dict:
    """Stage 3: Practical applicability and implementation assessment"""
    # Check cache first
    cached_result = get_cached_analysis(title, abstract, "practical")
    if cached_result:
        return cached_result
    
    try:
        model = GenerativeModel("gemini-1.5-flash")
        json_structure = '''
{
  "practicalApplicability": "high",
  "implementationComplexity": "medium",
  "hasCode": true,
  "difficultyLevel": "intermediate",
  "readingTime": 12
}
'''
        prompt = (
            "You are a practical AI engineer assessing the real-world applicability of this research. "
            "Focus on implementation feasibility and practical value.\n\n"
            "Title: {}\n\nAbstract: {}\n\n"
            "Provide practical assessment:\n\n"
            "PRACTICAL APPLICABILITY:\n"
            "- How useful is this for real-world applications? (high/medium/low)\n"
            "- What practical problems does this solve?\n"
            "- Is this production-ready or research prototype level?\n\n"
            "IMPLEMENTATION COMPLEXITY:\n"
            "- How difficult to implement from scratch? (low/medium/high)\n"
            "- What specialized knowledge/tools are required?\n"
            "- Are there likely to be available implementations?\n\n"
            "ACCESSIBILITY:\n"
            "- What skill level needed to understand this? (beginner/intermediate/advanced)\n"
            "- Realistic time to read and understand the full paper (minutes)\n"
            "- Likelihood of code/implementation being available (true/false)\n\n"
            "Return JSON: {}"
        ).format(title, abstract, json_structure)
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        # Cache the result
        cache_analysis(title, abstract, result, "practical")
        return result
    except Exception as e:
        print(f"Error in practical assessment: {e}")
        return {
            "practicalApplicability": "medium",
            "implementationComplexity": "medium",
            "hasCode": False,
            "difficultyLevel": "intermediate",
            "readingTime": 10
        }

async def generate_basic_summary(abstract: str, title: str) -> dict:
    """Stage 4: Generate basic summary and novelty assessment"""
    # Check cache first
    cached_result = get_cached_analysis(title, abstract, "summary")
    if cached_result:
        return cached_result
    
    try:
        model = GenerativeModel("gemini-1.5-flash")
        json_structure = '''
{
  "summary": "A concise, one-paragraph summary of the abstract.",
  "keyContribution": "A single sentence describing the core contribution of the paper.",
  "novelty": "A single sentence explaining what is novel about this work."
}
'''
        prompt = (
            "You are an expert summarizer creating concise insights for busy AI researchers.\n\n"
            "Title: {}\n\nAbstract: {}\n\n"
            "Provide:\n"
            "- SUMMARY: One clear paragraph explaining what this paper does\n"
            "- KEY CONTRIBUTION: One sentence capturing the main contribution\n"
            "- NOVELTY: One sentence explaining what's new/different\n\n"
            "Return JSON: {}"
        ).format(title, abstract, json_structure)
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        # Cache the result
        cache_analysis(title, abstract, result, "summary")
        return result
    except Exception as e:
        print(f"Error in basic summary: {e}")
        return {
            "summary": "Could not generate summary due to an error.",
            "keyContribution": "N/A",
            "novelty": "N/A"
        }

async def generate_summary(abstract: str, title: str) -> dict:
    """Multi-stage analysis pipeline for comprehensive paper understanding"""
    # Check if full analysis is cached
    cached_result = get_cached_analysis(title, abstract, "full")
    if cached_result:
        return cached_result
    
    try:
        print(f"Starting multi-stage analysis for: {title}")
        
        # Run all analysis stages in parallel for speed
        stage1_task = generate_technical_analysis(abstract, title)
        stage2_task = generate_research_context(abstract, title)
        stage3_task = generate_practical_assessment(abstract, title)
        stage4_task = generate_basic_summary(abstract, title)
        
        # Wait for all stages to complete
        technical, context, practical, basic = await asyncio.gather(
            stage1_task, stage2_task, stage3_task, stage4_task,
            return_exceptions=True
        )
        
        # Combine all analysis results
        combined_result = {}
        
        # Add basic summary
        if isinstance(basic, dict):
            combined_result.update(basic)
        else:
            combined_result.update({
                "summary": "Summary generation failed.",
                "keyContribution": "N/A",
                "novelty": "N/A"
            })
        
        # Add technical analysis
        if isinstance(technical, dict):
            combined_result.update(technical)
        else:
            combined_result.update({
                "technicalInnovation": "Technical analysis failed.",
                "methodologyBreakdown": "Methodology analysis failed.",
                "performanceHighlights": "Performance analysis failed.",
                "implementationInsights": "Implementation analysis failed.",
                "limitations": "Limitations analysis failed.",
                "reproductionDifficulty": "medium"
            })
        
        # Add research context
        if isinstance(context, dict):
            combined_result.update(context)
        else:
            combined_result.update({
                "researchContext": "Research context analysis failed.",
                "futureImplications": "Future implications analysis failed.",
                "researchSignificance": "incremental",
                "impactScore": 3.0
            })
        
        # Add practical assessment
        if isinstance(practical, dict):
            combined_result.update(practical)
        else:
            combined_result.update({
                "practicalApplicability": "medium",
                "implementationComplexity": "medium",
                "hasCode": False,
                "difficultyLevel": "intermediate",
                "readingTime": 10
            })
        
        print(f"Multi-stage analysis completed for: {title}")
        
        # Cache the complete analysis result
        cache_analysis(title, abstract, combined_result, "full")
        return combined_result
        
    except Exception as e:
        print(f"Error in multi-stage analysis: {e}")
        return {
            "summary": "Could not generate analysis due to an error.",
            "keyContribution": "N/A",
            "novelty": "N/A",
            "technicalInnovation": "Analysis unavailable due to processing error.",
            "methodologyBreakdown": "Analysis unavailable due to processing error.",
            "performanceHighlights": "Analysis unavailable due to processing error.",
            "implementationInsights": "Analysis unavailable due to processing error.",
            "researchContext": "Analysis unavailable due to processing error.",
            "futureImplications": "Analysis unavailable due to processing error.",
            "limitations": "Analysis unavailable due to processing error.",
            "impactScore": 3.0,
            "difficultyLevel": "intermediate",
            "readingTime": 10,
            "hasCode": False,
            "implementationComplexity": "medium",
            "practicalApplicability": "medium",
            "researchSignificance": "incremental",
            "reproductionDifficulty": "medium"
        }

async def batch_generate_summaries(papers_data: list) -> list:
    """Batch process multiple papers for analysis"""
    print(f"Starting batch analysis for {len(papers_data)} papers")
    
    # Create tasks for all papers
    tasks = []
    for paper in papers_data:
        task = generate_summary(paper['abstract'], paper['title'])
        tasks.append(task)
    
    # Process all papers concurrently with a reasonable limit
    batch_size = 5  # Process 5 papers at a time to avoid API rate limits
    results = []
    
    for i in range(0, len(tasks), batch_size):
        batch_tasks = tasks[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(tasks) + batch_size - 1)//batch_size}")
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Small delay between batches to respect API limits
        if i + batch_size < len(tasks):
            await asyncio.sleep(2)
    
    print(f"Batch analysis completed for {len(papers_data)} papers")
    return results

async def generate_and_save_summary(
    arxiv_id: str,
    original_summary: str,
    category: str,
    link: str,
    title: str,
    authors: list,
    published_dt: datetime
):
    db = SessionLocal() # Create a new session for the background task
    try:
        print(f"BACKGROUND: Generating AI summary for {title}")
        ai_summary_data = await generate_summary(original_summary, title)
        await asyncio.sleep(1) # Delay to respect Gemini API rate limits

        # Check if paper already exists (it might have been added by another concurrent request)
        existing_paper = db.query(Paper).filter(Paper.id == arxiv_id).first()

        if existing_paper:
            existing_paper.ai_summary_json = ai_summary_data
            existing_paper.fetched_at = datetime.utcnow()
        else:
            new_paper = Paper(
                id=arxiv_id,
                title=title,
                authors=authors,
                published=published_dt,
                original_summary=original_summary,
                ai_summary_json=ai_summary_data,
                category=category,
                link=link
            )
            db.add(new_paper)
        db.commit()
        print(f"BACKGROUND: Successfully saved AI summary for {title}")
    except Exception as e:
        print(f"BACKGROUND ERROR: Failed to generate or save summary for {title}: {e}")
    finally:
        db.close() # Close the session

@app.get("/papers")
async def get_papers(
    days: int = 7,
    category: str = "all",
    query: str = "",
    background_tasks: BackgroundTasks = BackgroundTasks(), # Add BackgroundTasks
    db: Session = Depends(get_db)
):
    print(f"DEBUG: /papers endpoint called with days={days}, category={category}, query='{query}'")
    # Calculate the date for filtering (e.g., 7 days ago)
    date_filter_dt = datetime.utcnow() - timedelta(days=days)

    category_query = ''
    if category == 'all':
        category_query = 'cat:cs.AI OR cat:cs.LG OR cat:cs.CV OR cat:cs.CL'
    else:
        category_query = f'cat:{category}'

    search_query_arxiv = f'({category_query})'
    if query:
        search_query_arxiv += f' AND (ti:"{query}" OR abs:"{query}")'

    arxiv_api_url = f'http://export.arxiv.org/api/query?search_query={search_query_arxiv}&sortBy=submittedDate&sortOrder=descending&max_results=10'

    print(f'DEBUG: arXiv API URL: {arxiv_api_url}')

    try:
        response = requests.get(arxiv_api_url)
        print(f"DEBUG: arXiv API Response Status: {response.status_code}")
        response.raise_for_status()
        xml_text = response.text
        parsed_xml = xmltodict.parse(xml_text)

        entries = parsed_xml['feed'].get('entry', [])
        if not isinstance(entries, list): # Handle single entry case
            entries = [entries]

        papers_to_return = []
        for entry in entries:
            arxiv_id = entry['id']
            title = entry['title']
            authors = [author['name'] for author in entry['author']] if isinstance(entry['author'], list) else [entry['author']['name']]
            published_str = entry['published']
            published_dt = datetime.strptime(published_str, '%Y-%m-%dT%H:%M:%SZ')
            original_summary = entry['summary']
            link = next((l['@href'] for l in entry['link'] if l['@rel'] == 'alternate'), None)

            # Check cache
            cached_paper = db.query(Paper).filter(Paper.id == arxiv_id).first()

            ai_summary_data = None
            if cached_paper and cached_paper.ai_summary_json and cached_paper.fetched_at > (datetime.utcnow() - timedelta(days=1)):
                # Use cached AI summary if less than 24 hours old
                ai_summary_data = cached_paper.ai_summary_json
                print(f"DEBUG: Using cached AI summary for {title}")
            else:
                # Add task to background to generate and save summary
                background_tasks.add_task(
                    generate_and_save_summary,
                    arxiv_id,
                    original_summary,
                    category,
                    link,
                    title,
                    authors,
                    published_dt,
                    db # Pass the session to the background task
                )
                # Return a placeholder for now
                ai_summary_data = {
                    "summary": "Summary pending...",
                    "keyContribution": "Pending...",
                    "novelty": "Pending..."
                }
                print(f"DEBUG: Added background task for {title}")
                
            papers_to_return.append({
                "id": arxiv_id,
                "title": title,
                "authors": authors,
                "published": published_str, # Return as string for frontend consistency
                "summary": original_summary,
                "aiSummary": ai_summary_data,
                "link": link
            })
        
        print(f"DEBUG: Returning {len(papers_to_return)} papers to frontend.")
        return papers_to_return

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error fetching from arXiv: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching from arXiv: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/papers/trends")
async def get_paper_trends(
    category: str = "all",
    db: Session = Depends(get_db)
):
    category_query = ''
    if category == 'all':
        category_query = 'cat:cs.AI OR cat:cs.LG OR cat:cs.CV OR cat:cs.CL'
    else:
        category_query = f'cat:{category}'

    # Fetch more papers for trend analysis (e.g., 50)
    arxiv_api_url = f'http://export.arxiv.org/api/query?search_query={category_query}&sortBy=submittedDate&sortOrder=descending&max_results=50'

    try:
        response = requests.get(arxiv_api_url)
        response.raise_for_status()
        xml_text = response.text
        parsed_xml = xmltodict.parse(xml_text)

        entries = parsed_xml['feed'].get('entry', [])
        if not isinstance(entries, list):
            entries = [entries]

        papers_for_analysis = []
        for entry in entries:
            arxiv_id = entry['id']
            title = entry['title']
            original_summary = entry['summary']

            cached_paper = db.query(Paper).filter(Paper.id == arxiv_id).first()
            ai_summary_data = None

            if cached_paper and cached_paper.ai_summary_json and cached_paper.fetched_at > (datetime.utcnow() - timedelta(days=1)):
                ai_summary_data = cached_paper.ai_summary_json
            else:
                ai_summary_data = await generate_summary(original_summary)
                if cached_paper:
                    cached_paper.ai_summary_json = ai_summary_data
                    cached_paper.fetched_at = datetime.utcnow()
                else:
                    # If not in cache, add a minimal entry for trend analysis
                    new_paper = Paper(
                        id=arxiv_id,
                        title=title,
                        authors=[], # Not needed for trend analysis
                        published=datetime.utcnow(),
                        original_summary=original_summary,
                        ai_summary_json=ai_summary_data,
                        category=category,
                        link="" # Not needed for trend analysis
                    )
                    db.add(new_paper)
                db.commit()
                db.refresh(cached_paper or new_paper)

            papers_for_analysis.append({"title": title, "summary": ai_summary_data.get("summary", original_summary)})

        if not papers_for_analysis:
            return {"trendAnalysis": "No papers found to analyze for trends."}

        # Generate trend analysis using Gemini
        model = GenerativeModel("gemini-1.5-flash")
        papers_formatted = "\n".join([f"- Title: {p['title']}\n  Summary: {p['summary']}" for p in papers_for_analysis])
        prompt = (
            "As an expert AI research analyst, your task is to identify high-level trends from a list of recent research paper titles and summaries.\n"
            "Based on the provided list of papers, please generate a concise report that covers the following points:\n\n"
            "1.  **Key Themes:** Identify 2-4 dominant themes or sub-fields that are emerging or highly active.\n"
            "2.  **Common Techniques:** What are the most frequently mentioned models, architectures, or methods?\n"
            "3.  **Overall Summary:** Provide a brief, high-level narrative of the current research direction in this area based on the papers.\n\n"
            "Here are the papers:\n{}\n\n"
            "**Trend Analysis Report:**"
        ).format(papers_formatted)
        response = await model.generate_content_async(prompt)
        trend_analysis_text = response.text

        return {"trendAnalysis": trend_analysis_text}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from arXiv: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/papers/contextual-search")
async def contextual_search(
    request: dict,
    db: Session = Depends(get_db)
):
    user_description = request.get("description", "")
    if not user_description:
        raise HTTPException(status_code=400, detail="Project description cannot be empty.")

    try:
        # 1. Deconstruct user query with Gemini
        model = GenerativeModel("gemini-1.5-flash")
        deconstruct_prompt = (f'''Analyze the following user project description and extract the key information needed to find relevant academic papers. 
        Identify the main problem, the domain, and any specific technologies or methodologies mentioned.\n\n
        User Description: "{user_description}"\n\n
        Return a JSON object with the following keys: "problem", "domain", "technologies", "search_query".
        The 'search_query' should be a concise string of 3-5 keywords suitable for a semantic search on arXiv.''')

        deconstruct_response = await model.generate_content_async(deconstruct_prompt)
        deconstructed_info = json.loads(deconstruct_response.text.replace("```json", "").replace("```", "").strip())
        search_query = deconstructed_info.get("search_query", "")

        if not search_query:
            raise HTTPException(status_code=500, detail="Could not generate a search query from the description.")

        # 2. Search arXiv with the generated query
        arxiv_api_url = f'http://export.arxiv.org/api/query?search_query=all:"{search_query}"&sortBy=relevance&sortOrder=descending&max_results=10'
        response = requests.get(arxiv_api_url)
        response.raise_for_status()
        parsed_xml = xmltodict.parse(response.text)
        entries = parsed_xml['feed'].get('entry', [])
        if not isinstance(entries, list):
            entries = [entries]

        # 3. Summarize and analyze the top papers
        papers_for_analysis = []
        for entry in entries:
            papers_for_analysis.append({
                "title": entry['title'],
                "summary": entry['summary'],
                "id": entry['id']
            })

        if not papers_for_analysis:
            return {"analysis": "No relevant papers found for your project description.", "papers": []}

        papers_formatted = "\n".join([f"- Title: {p['title']}\n  Summary: {p['summary']}" for p in papers_for_analysis])

        synthesis_prompt = (f'''You are an expert AI research assistant. A user has described a project they are working on. 
        Based on their goal and a list of relevant research papers, your task is to synthesize the information and provide actionable advice.\n\n
        User's Project Goal: "{user_description}"\n\n
        Relevant Research Papers:\n{papers_formatted}\n\n
        Please provide a concise analysis that includes:\n
        1. **State-of-the-Art Techniques:** Briefly describe 2-3 of the most cutting-edge techniques from these papers that are directly applicable to the user's project.\n
        2. **How to Apply Them:** For each technique, explain how the user could specifically implement or adapt it for their application.\n
        3. **Potential Challenges:** Mention any potential challenges or limitations the user should be aware of when using these advanced methods.\n\n
        **Analysis Report:**''')

        synthesis_response = await model.generate_content_async(synthesis_prompt)
        analysis_text = synthesis_response.text

        return {"analysis": analysis_text, "papers": papers_for_analysis}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from arXiv: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in contextual_search: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# Pydantic models for batch processing
class PaperData(BaseModel):
    title: str
    abstract: str
    arxiv_id: str = None

class BatchAnalysisRequest(BaseModel):
    papers: List[PaperData]

@app.post("/papers/batch-analyze")
async def batch_analyze_papers(request: BatchAnalysisRequest):
    """Batch analyze multiple papers for comprehensive insights"""
    try:
        if not request.papers:
            raise HTTPException(status_code=400, detail="No papers provided for analysis")
        
        if len(request.papers) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 papers allowed per batch")
        
        print(f"Starting batch analysis for {len(request.papers)} papers")
        
        # Convert to the format expected by batch_generate_summaries
        papers_data = []
        for paper in request.papers:
            papers_data.append({
                'title': paper.title,
                'abstract': paper.abstract,
                'arxiv_id': paper.arxiv_id
            })
        
        # Process all papers using our batch function
        analysis_results = await batch_generate_summaries(papers_data)
        
        # Combine paper data with analysis results
        response_data = []
        for i, paper in enumerate(request.papers):
            analysis = analysis_results[i] if i < len(analysis_results) else None
            
            if isinstance(analysis, Exception):
                analysis = {
                    "summary": f"Analysis failed: {str(analysis)}",
                    "keyContribution": "N/A",
                    "novelty": "N/A",
                    "technicalInnovation": "Analysis failed",
                    "methodologyBreakdown": "Analysis failed",
                    "performanceHighlights": "Analysis failed",
                    "implementationInsights": "Analysis failed",
                    "researchContext": "Analysis failed",
                    "futureImplications": "Analysis failed",
                    "limitations": "Analysis failed",
                    "impactScore": 3.0,
                    "difficultyLevel": "intermediate",
                    "readingTime": 10,
                    "hasCode": False,
                    "implementationComplexity": "medium",
                    "practicalApplicability": "medium",
                    "researchSignificance": "incremental",
                    "reproductionDifficulty": "medium"
                }
            
            response_data.append({
                "title": paper.title,
                "abstract": paper.abstract,
                "arxiv_id": paper.arxiv_id,
                "analysis": analysis
            })
        
        print(f"Batch analysis completed successfully for {len(request.papers)} papers")
        return {"results": response_data, "total_processed": len(response_data)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "redis_connected": redis_client is not None,
        "gemini_configured": bool(GEMINI_API_KEY)
    }