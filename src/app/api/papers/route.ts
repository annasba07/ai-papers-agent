import { NextResponse } from 'next/server';
import { parseStringPromise } from 'xml2js';
import { GoogleGenerativeAI } from '@google/generative-ai';

// IMPORTANT: Replace with your actual API key
const API_KEY = process.env.GEMINI_API_KEY;
console.log('Using Gemini API Key:', API_KEY ? 'Loaded from .env.local' : 'Not Loaded');

const genAI = new GoogleGenerativeAI(API_KEY || '');

async function generateSummary(abstract: string): Promise<any> {
  if (!API_KEY) {
    console.log('GEMINI_API_KEY is not configured.');
    return {
      summary: "AI summary disabled. API key not configured.",
      keyContribution: "N/A",
      novelty: "N/A"
    };
  }
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    const prompt = `Analyze the following research paper abstract and provide a structured summary.

Abstract:
${abstract}

Please return a JSON object with the following structure:
{
  "summary": "A concise, one-paragraph summary of the abstract.",
  "keyContribution": "A single sentence describing the core contribution of the paper.",
  "novelty": "A single sentence explaining what is novel about this work."
}
`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    console.log('Raw Gemini Response:', text); // Log the raw response
    // Clean the response to ensure it's valid JSON
    const cleanedText = text.replace(/```json|```/g, '').trim();
    return JSON.parse(cleanedText);
  } catch (error) {
    console.error("Error generating summary:", error); // Log the full error
    return {
      summary: "Could not generate summary due to an error.",
      keyContribution: "N/A",
      novelty: "N/A"
    };
  }
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get('days') || '7');
  const category = searchParams.get('category') || 'all';
  const query = searchParams.get('query') || '';

  // Calculate the date for filtering (e.g., 7 days ago)
  const date = new Date();
  date.setDate(date.getDate() - days);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const dateFilter = `submittedDate:[${year}${month}${day}0000 TO *]`;

  let categoryQuery = '';
  if (category === 'all') {
    categoryQuery = 'cat:cs.AI OR cat:cs.LG OR cat:cs.CV OR cat:cs.CL';
  } else {
    categoryQuery = `cat:${category}`;
  }

  let searchQuery = `(${categoryQuery})`;
  if (query) {
    searchQuery += ` AND (ti:"${query}" OR abs:"${query}")`;
  }

  const arxivApiUrl = `http://export.arxiv.org/api/query?search_query=${searchQuery}&sortBy=submittedDate&sortOrder=descending&max_results=10`;

  console.log('arXiv API URL:', arxivApiUrl);

  try {
    const response = await fetch(arxivApiUrl);
    if (!response.ok) {
      throw new Error(`arXiv API returned status ${response.status}`);
    }
    const xmlText = await response.text();
    const result = await parseStringPromise(xmlText);

    const entries = result.feed.entry || [];
    const papers = await Promise.all(entries.map(async (entry: any) => {
      const summary = entry.summary[0];
      const aiSummaryObject = await generateSummary(summary);
      return {
        id: entry.id[0],
        title: entry.title[0],
        authors: entry.author ? entry.author.map((a: any) => a.name[0]) : [],
        published: entry.published[0],
        summary: summary, // Keep original summary
        aiSummary: aiSummaryObject, // Add AI-generated summary object
        link: entry.link.find((l: any) => l.$.rel === 'alternate').$.href,
      };
    }));

    console.log(`Fetched ${papers.length} papers.`);
    return NextResponse.json(papers);
  } catch (error: any) {
    console.error('Error fetching papers from arXiv:', error.message, error.stack);
    return NextResponse.json({ error: 'Failed to fetch papers', details: error.message }, { status: 500 });
  }
}