from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
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

async def generate_summary(abstract: str, title: str) -> dict:
    try:
        model = GenerativeModel("gemini-1.5-flash")
        json_structure = '''
{
  "summary": "A concise, one-paragraph summary of the abstract.",
  "keyContribution": "A single sentence describing the core contribution of the paper.",
  "novelty": "A single sentence explaining what is novel about this work.",
  "technicalInnovation": "Detailed explanation of the core technical mechanism or approach.",
  "methodologyBreakdown": "Step-by-step breakdown of how the proposed method works.",
  "performanceHighlights": "Key performance results and what makes them significant.",
  "implementationInsights": "Practical insights about implementation complexity and requirements.",
  "researchContext": "How this work relates to and builds upon existing research.",
  "futureImplications": "What this enables for future research or applications.",
  "limitations": "Key limitations or potential issues with the approach.",
  "impactScore": 4.2,
  "difficultyLevel": "intermediate",
  "readingTime": 12,
  "hasCode": true,
  "implementationComplexity": "medium",
  "practicalApplicability": "high",
  "researchSignificance": "breakthrough",
  "reproductionDifficulty": "medium"
}
'''
        prompt = (
            "You are an expert AI researcher analyzing a paper for rapid comprehension. Your goal is to help researchers "
            "understand this paper extremely quickly and decide if it's worth reading fully.\n\n"
            "Title: {}\n\n"
            "Abstract: {}\n\n"
            "Provide a comprehensive analysis that enables 2-3 minute deep understanding. Focus on:\n\n"
            "TECHNICAL DEPTH:\n"
            "- What specific technical innovation is introduced?\n"
            "- How does the core mechanism/algorithm work?\n"
            "- What are the key mathematical or architectural insights?\n\n"
            "METHODOLOGY:\n"
            "- Break down the approach step-by-step\n"
            "- Explain the key algorithmic or design choices\n"
            "- Identify what makes this approach different from existing methods\n\n"
            "PERFORMANCE & IMPACT:\n"
            "- What are the key results and why are they significant?\n"
            "- How does this compare to previous state-of-the-art?\n"
            "- What performance gains or capabilities does this enable?\n\n"
            "IMPLEMENTATION REALITY:\n"
            "- What would it actually take to implement this?\n"
            "- What are the computational/resource requirements?\n"
            "- What are likely implementation challenges or gotchas?\n\n"
            "RESEARCH POSITIONING:\n"
            "- How does this build on or differ from existing work?\n"
            "- What research trajectory does this represent?\n"
            "- What future work does this enable or suggest?\n\n"
            "Please return a JSON object with the following structure:\n{}\n\n"
            "Scoring Guidelines:\n"
            "- impactScore: 1-5 scale (1=incremental, 5=breakthrough)\n"
            "- difficultyLevel: 'beginner', 'intermediate', or 'advanced'\n"
            "- readingTime: realistic minutes to read and understand the full paper\n"
            "- hasCode: likely availability of implementation code\n"
            "- implementationComplexity: 'low', 'medium', or 'high'\n"
            "- practicalApplicability: 'low', 'medium', or 'high'\n"
            "- researchSignificance: 'incremental', 'significant', or 'breakthrough'\n"
            "- reproductionDifficulty: 'low', 'medium', or 'high'"
        ).format(title, abstract, json_structure)
        response = await model.generate_content_async(prompt)
        text = response.text
        cleaned_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {
            "summary": "Could not generate summary due to an error.",
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