# UX Assessment: AI Paper Atlas
**Persona:** Prof. James Williams, MIT CSAIL
**Date:** December 16, 2025
**Assessment Duration:** ~15 minutes
**Scenario:** Preparing graduate seminar on efficient language models

---

## Overall Rating: 5/10

As a professor preparing curriculum, I need tools that help me distinguish foundational work from incremental advances, identify pedagogically valuable papers, and build coherent learning progressions. AI Paper Atlas shows promise but falls short of being seminar-ready.

---

## Teaching Utility Assessment

### What Works

**1. Search Functionality (7/10)**
- The semantic search successfully returned 6 highly relevant papers on "efficient language models"
- Papers covered key techniques: distillation, pruning, quantization, optimization
- Search was reasonably fast (8 seconds) and showed clear relevance
- Good coverage of recent work in the efficiency domain

**2. Filtering System (6/10)**
- Difficulty levels (Beginner/Intermediate/Advanced/Expert) are pedagogically valuable
- Category filters (cs.CL, cs.CV, etc.) work as expected
- "Intermediate" filter expanded results from 6 to 22 papers - useful for finding student-appropriate material
- Combined filters work well together

**3. Paper Presentation (5/10)**
- TL;DR summaries are helpful for quick scanning
- Full abstracts available on expansion
- ArXiv links provided for deep reading
- Basic metadata present (though dates showed "Invalid Date" for some papers)

### Critical Weaknesses for Teaching Use

**1. No Foundational vs. Incremental Distinction**
The tool provides no way to identify:
- Seminal papers that students must read (e.g., where is BERT? Attention is All You Need?)
- Survey papers that provide overview
- Novel techniques vs. minor improvements
- Citation impact or influence metrics

I asked the Research Advisor explicitly: "Can you help me identify which papers are foundational vs incremental?" The response was generic and unhelpful - just listing papers with "inspect its methodology" without any actual analysis of their foundational status.

**2. Research Advisor Limitations**
- Responded with "Contextual synthesis temporarily unavailable"
- Provided basic paper lists instead of pedagogical guidance
- No understanding of curriculum building needs
- Suggested follow-up questions were technical ("How do these methods scale?") rather than educational ("Which should students read first?")

**3. Missing Pedagogical Features**
No indication of:
- Paper clarity/readability (crucial for student assignments)
- Quality of figures/visualizations
- Availability of code implementations
- Prerequisites or background knowledge needed
- Related tutorials or lecture materials

**4. No Reading List Organization**
Cannot:
- Save papers to a curated list
- Arrange papers in pedagogical order
- Export reading lists for students
- Annotate papers with teaching notes
- Share lists with TAs or students

**5. Limited Historical Context**
- Only shows recent papers (most from 2025)
- Where are the foundational works (2017-2019 era)?
- No clear temporal visualization showing how the field evolved
- Cannot filter by "highly cited" or "influential"

---

## Student Recommendation Potential: 3/10

**Would I recommend this to my graduate students?** Only with significant caveats.

**Positives:**
- Good for discovering recent work in a specific area
- Difficulty filters help find appropriate reading level
- Clean interface, easy to navigate

**Negatives:**
- No way to distinguish must-read papers from nice-to-know
- Missing citation counts and impact metrics
- Cannot build structured reading lists
- No guidance on prerequisites or reading order
- Limited to very recent papers

**What students actually need:**
1. Clear identification of seminal papers
2. Learning paths from basics to advanced
3. Papers with good pedagogical value (clear writing, good figures)
4. Code repositories and tutorials
5. Connections between papers (builds on, extends, contradicts)

---

## Specific Strengths

1. **Fast semantic search** - Found relevant papers quickly
2. **Difficulty tagging** - Valuable for matching papers to student level
3. **Clean UI** - No clutter, easy to scan results
4. **TL;DR summaries** - Efficient for initial screening
5. **Category filters work well** - Easy to narrow by research area

---

## Specific Weaknesses

1. **Date inconsistency** - Many papers showed "Invalid Date"
2. **No citation metrics** - Cannot assess impact or importance
3. **Advisor gives generic responses** - Not contextually aware or pedagogically focused
4. **No foundational paper identification** - Critical for curriculum building
5. **No list curation features** - Cannot save or organize for teaching
6. **Missing key papers** - Where are BERT, DistilBERT, etc.?
7. **No paper relationships** - Cannot see citation networks or build dependencies
8. **Limited export options** - Cannot share reading lists with students

---

## Would I Use This for My Seminar?

**No, not in its current form.**

Here's what I'd do instead:
1. Use Google Scholar for citation counts and foundational papers
2. Use Semantic Scholar for paper relationships and influence
3. Manually curate based on my field knowledge
4. Ask colleagues for their reading lists
5. Check conference tutorial materials

**I might use AI Paper Atlas for:**
- Quick scoping of very recent work (last 3-6 months)
- Finding papers in adjacent areas I'm less familiar with
- Getting TL;DR summaries to decide what to read in detail

**I would not use it for:**
- Building comprehensive reading lists
- Identifying foundational papers
- Understanding field evolution
- Assessing pedagogical value

---

## Recommendations for Improvement

### High Priority (Blockers for Teaching Use)

1. **Add citation metrics and impact scores**
   - Citation count
   - Influential citations (semantic scholar)
   - "Highly cited" badge for papers above threshold
   - Temporal citation trends

2. **Identify foundational papers**
   - Tag seminal works in each area
   - "Must-read" designation
   - Survey paper identification
   - Historical context (when technique was introduced)

3. **Build reading list functionality**
   - Save papers to named lists
   - Reorder papers pedagogically
   - Add instructor notes
   - Export to various formats (BibTeX, markdown, PDF)
   - Share lists with students

4. **Enhance Research Advisor for teaching**
   - Understand pedagogical queries
   - Suggest reading progressions
   - Identify prerequisites
   - Recommend foundational → advanced paths

### Medium Priority (Would Significantly Improve)

5. **Paper quality indicators**
   - Readability scores
   - Code availability (with links)
   - Tutorial/blog post availability
   - Figure quality indicators

6. **Relationship visualization**
   - Citation networks
   - "Builds on" relationships
   - Paper genealogy
   - Technique evolution timelines

7. **Temporal controls**
   - Filter by publication year
   - "Classics" vs "Recent" toggle
   - Timeline view of field development

8. **Fix date display issues**
   - Many papers showed "Invalid Date"
   - Needs consistent, accurate metadata

### Lower Priority (Nice to Have)

9. **Student-focused features**
   - Paper difficulty explanations (why is this "intermediate"?)
   - Background knowledge prerequisites listed
   - Recommended companion papers
   - Discussion questions for each paper

10. **Collaboration features**
    - Share lists with co-instructors
    - Collaborative annotation
    - Student feedback on difficulty/clarity

---

## Comparison to Existing Tools

**vs. Google Scholar:**
- Scholar has citations, influence, "cited by" - critical for teaching
- Atlas has better semantic search and modern UI
- **Winner: Scholar for teaching**

**vs. Semantic Scholar:**
- Semantic Scholar has influence metrics, "highly influential" citations
- S2 has paper summaries and TLDRs (similar quality)
- S2 shows citation context
- **Winner: Semantic Scholar for teaching**

**vs. Papers with Code:**
- PWC links papers to implementations and benchmarks
- PWC has leaderboards showing SOTA
- Atlas has broader coverage beyond benchmarked tasks
- **Winner: PWC for practical/implementation courses**

**vs. arXiv Sanity:**
- Sanity allows custom libraries and tagging
- Sanity has recommendation engine based on reading history
- Atlas has better search
- **Winner: arXiv Sanity for personal curation**

---

## Final Thoughts

As someone who teaches graduate seminars and maintains reading lists for students, I need tools that help me separate signal from noise, identify must-read papers, and build coherent learning progressions. AI Paper Atlas feels built for researchers tracking cutting-edge work, not for educators building curriculum.

The semantic search is good. The UI is clean. But without citation metrics, foundational paper identification, list curation, or pedagogical guidance, it's not ready for my classroom.

**I would use it as a supplementary discovery tool, not a primary resource for curriculum building.**

The Research Advisor, in particular, was disappointing. When I explicitly asked for help distinguishing foundational from incremental work - a core teaching need - it gave me generic paper lists and told me to "inspect methodologies." That's not helpful. I need the system to understand that some papers (BERT, GPT, Transformer) are foundational and must be taught before others.

**Bottom line:** Promising search technology, but needs significant pedagogical features before I'd recommend it to my students or use it for seminar prep.

---

## Key Quote

*"The field moves too fast - I need tools that help me identify what's actually important, not just what's recent. Show me the papers my students need to understand the field, not just the papers from this week."*

---

**Assessment completed:** December 16, 2025
**Would reassess after:** Citation metrics added, reading list functionality implemented
