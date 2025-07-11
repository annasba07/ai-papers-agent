"""
PDF Extraction Service
Handles downloading, parsing, and extracting structured content from research papers
"""
import logging
import asyncio
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import tempfile
import os

import httpx
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image

from ..models.paper import ExtractedSection, ExtractedFigure
from ..core.config import settings

logger = logging.getLogger(__name__)

class PDFExtractionService:
    """Service for extracting structured content from PDF papers"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_paper_digest_pdfs"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Common section patterns in academic papers
        self.section_patterns = [
            r'^\s*(\d+\.?\s*)?abstract\s*$',
            r'^\s*(\d+\.?\s*)?introduction\s*$',
            r'^\s*(\d+\.?\s*)?related\s+work\s*$',
            r'^\s*(\d+\.?\s*)?methodology\s*$',
            r'^\s*(\d+\.?\s*)?method\s*$',
            r'^\s*(\d+\.?\s*)?approach\s*$',
            r'^\s*(\d+\.?\s*)?experiments?\s*$',
            r'^\s*(\d+\.?\s*)?results?\s*$',
            r'^\s*(\d+\.?\s*)?evaluation\s*$',
            r'^\s*(\d+\.?\s*)?discussion\s*$',
            r'^\s*(\d+\.?\s*)?conclusion\s*$',
            r'^\s*(\d+\.?\s*)?future\s+work\s*$',
            r'^\s*(\d+\.?\s*)?limitations\s*$',
            r'^\s*(\d+\.?\s*)?references\s*$',
            r'^\s*(\d+\.?\s*)?appendix\s*$'
        ]
        
        # Figure and table patterns
        self.figure_patterns = [
            r'(figure|fig\.?)\s*(\d+)',
            r'(table|tab\.?)\s*(\d+)',
            r'(equation|eq\.?)\s*(\d+)'
        ]
    
    async def download_pdf(self, pdf_url: str, paper_id: str) -> Optional[Path]:
        """
        Download PDF from URL and save temporarily
        
        Args:
            pdf_url: URL to download PDF from
            paper_id: Paper ID for filename
            
        Returns:
            Path to downloaded PDF file or None if failed
        """
        try:
            pdf_path = self.temp_dir / f"{paper_id}.pdf"
            
            # Skip if already downloaded
            if pdf_path.exists():
                logger.info(f"PDF already exists for {paper_id}")
                return pdf_path
            
            logger.info(f"Downloading PDF for {paper_id} from {pdf_url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                
                # Save PDF to temp directory
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Downloaded PDF for {paper_id}: {pdf_path}")
                return pdf_path
                
        except Exception as e:
            logger.error(f"Failed to download PDF for {paper_id}: {e}")
            return None
    
    async def extract_full_text(self, pdf_path: Path) -> str:
        """
        Extract full text from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Full text content
        """
        try:
            full_text = ""
            
            # Open PDF with PyMuPDF
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Clean up text
                text = self._clean_text(text)
                full_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
            
            doc.close()
            
            logger.info(f"✅ Extracted {len(full_text)} characters from {pdf_path}")
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    async def extract_sections(self, full_text: str) -> Dict[str, ExtractedSection]:
        """
        Extract structured sections from full text
        
        Args:
            full_text: Full paper text
            
        Returns:
            Dictionary of section name -> ExtractedSection
        """
        try:
            sections = {}
            lines = full_text.split('\n')
            current_section = None
            current_content = []
            
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                
                # Check if line matches a section pattern
                section_match = None
                for pattern in self.section_patterns:
                    if re.match(pattern, line_clean, re.IGNORECASE):
                        section_match = line_clean
                        break
                
                if section_match:
                    # Save previous section if exists
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if content:
                            sections[current_section] = ExtractedSection(
                                section_name=current_section,
                                content=content,
                                page_numbers=self._extract_page_numbers(content)
                            )
                    
                    # Start new section
                    current_section = self._normalize_section_name(section_match)
                    current_content = []
                else:
                    # Add to current section
                    if current_section:
                        current_content.append(line)
            
            # Save last section
            if current_section and current_content:
                content = '\n'.join(current_content).strip()
                if content:
                    sections[current_section] = ExtractedSection(
                        section_name=current_section,
                        content=content,
                        page_numbers=self._extract_page_numbers(content)
                    )
            
            logger.info(f"✅ Extracted {len(sections)} sections: {list(sections.keys())}")
            return sections
            
        except Exception as e:
            logger.error(f"Failed to extract sections: {e}")
            return {}
    
    async def extract_figures_and_tables(self, pdf_path: Path, full_text: str) -> List[ExtractedFigure]:
        """
        Extract figures, tables, and equations from PDF
        
        Args:
            pdf_path: Path to PDF file
            full_text: Full text content
            
        Returns:
            List of extracted figures/tables
        """
        try:
            figures = []
            
            # Open PDF with PyMuPDF
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    # Try to find caption in text
                    caption = self._find_figure_caption(full_text, page_num + 1, "figure")
                    
                    figures.append(ExtractedFigure(
                        figure_type="figure",
                        caption=caption or f"Figure on page {page_num + 1}",
                        page_number=page_num + 1,
                        figure_number=f"fig_{page_num + 1}_{img_index}"
                    ))
                
                # Extract tables (basic detection)
                tables = page.find_tables()
                for table_index, table in enumerate(tables):
                    try:
                        # Extract table content
                        table_content = table.extract()
                        table_text = self._format_table_content(table_content)
                        
                        caption = self._find_figure_caption(full_text, page_num + 1, "table")
                        
                        figures.append(ExtractedFigure(
                            figure_type="table",
                            caption=caption or f"Table on page {page_num + 1}",
                            content=table_text,
                            page_number=page_num + 1,
                            figure_number=f"tab_{page_num + 1}_{table_index}"
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to extract table on page {page_num + 1}: {e}")
            
            doc.close()
            
            logger.info(f"✅ Extracted {len(figures)} figures/tables from {pdf_path}")
            return figures
            
        except Exception as e:
            logger.error(f"Failed to extract figures from {pdf_path}: {e}")
            return []
    
    async def process_paper_pdf(self, paper_id: str, pdf_url: str) -> Dict[str, Any]:
        """
        Complete PDF processing pipeline
        
        Args:
            paper_id: Paper ID
            pdf_url: URL to PDF
            
        Returns:
            Dictionary with extracted content
        """
        try:
            logger.info(f"Starting PDF processing for {paper_id}")
            
            # Download PDF
            pdf_path = await self.download_pdf(pdf_url, paper_id)
            if not pdf_path:
                return {"error": "Failed to download PDF"}
            
            # Extract full text
            full_text = await self.extract_full_text(pdf_path)
            if not full_text:
                return {"error": "Failed to extract text"}
            
            # Extract sections
            sections = await self.extract_sections(full_text)
            
            # Extract figures and tables
            figures = await self.extract_figures_and_tables(pdf_path, full_text)
            
            # Clean up temporary file
            try:
                os.remove(pdf_path)
            except Exception:
                pass
            
            result = {
                "full_text": full_text,
                "sections": sections,
                "figures": figures,
                "processing_stats": {
                    "text_length": len(full_text),
                    "sections_found": len(sections),
                    "figures_found": len(figures)
                }
            }
            
            logger.info(f"✅ Completed PDF processing for {paper_id}: {result['processing_stats']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF for {paper_id}: {e}")
            return {"error": str(e)}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\+\=\<\>\@\#\$\%\^\&\*]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\s*\n\s*', '\n', text)
        
        return text.strip()
    
    def _normalize_section_name(self, section_match: str) -> str:
        """Normalize section name for consistent keys"""
        # Remove numbers and clean up
        name = re.sub(r'^\d+\.?\s*', '', section_match)
        name = name.strip().lower()
        
        # Standardize common variations
        name_mapping = {
            "related work": "related_work",
            "future work": "future_work",
            "experiments": "experiments",
            "experiment": "experiments",
            "results": "results",
            "result": "results",
            "conclusions": "conclusion",
            "discussions": "discussion"
        }
        
        return name_mapping.get(name, name.replace(' ', '_'))
    
    def _extract_page_numbers(self, content: str) -> List[int]:
        """Extract page numbers from content (basic implementation)"""
        page_numbers = []
        
        # Look for page markers in content
        page_matches = re.findall(r'--- Page (\d+) ---', content)
        for match in page_matches:
            page_numbers.append(int(match))
        
        return sorted(list(set(page_numbers)))
    
    def _find_figure_caption(self, full_text: str, page_number: int, figure_type: str) -> Optional[str]:
        """Find caption for figure/table near specific page"""
        try:
            # Look for captions in the text
            pattern = f"({figure_type}|{figure_type[:3]}\.?)\s*(\d+)[:\.]?\s*([^\n]+)"
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            
            # Return first match (basic implementation)
            if matches:
                return matches[0][2].strip()
            
            return None
            
        except Exception:
            return None
    
    def _format_table_content(self, table_content: List[List[str]]) -> str:
        """Format extracted table content as readable text"""
        try:
            if not table_content:
                return ""
            
            # Simple table formatting
            formatted_rows = []
            for row in table_content:
                if row:  # Skip empty rows
                    formatted_rows.append(" | ".join(str(cell) for cell in row))
            
            return "\n".join(formatted_rows)
            
        except Exception:
            return ""
    
    async def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about PDF extraction system"""
        try:
            temp_files = list(self.temp_dir.glob("*.pdf"))
            
            return {
                "temp_directory": str(self.temp_dir),
                "temp_files_count": len(temp_files),
                "temp_files_size_mb": sum(f.stat().st_size for f in temp_files) / (1024 * 1024),
                "supported_formats": ["PDF"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get extraction stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary PDF files older than specified hours"""
        try:
            import time
            current_time = time.time()
            cleanup_threshold = current_time - (older_than_hours * 3600)
            
            cleaned_count = 0
            for pdf_file in self.temp_dir.glob("*.pdf"):
                if pdf_file.stat().st_mtime < cleanup_threshold:
                    try:
                        os.remove(pdf_file)
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove {pdf_file}: {e}")
            
            logger.info(f"✅ Cleaned up {cleaned_count} temporary PDF files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return 0

# Global PDF extraction service instance
pdf_extraction_service = PDFExtractionService()