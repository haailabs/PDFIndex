import os
import json
import time
from typing import Dict, Optional
import PyPDF2
import openai
from pathlib import Path

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class PaperProcessor:
    def __init__(self, groq_api_key: str):
        """Initialize the paper processor with Groq API credentials."""
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key
        )
        
        self.system_prompt = """You are a research paper metadata extractor. Given text from the first few pages of a paper, extract the following information:
- Title
- Authors (as a list)  
- Year
- Journal/Conference
- DOI (if available)
- Keywords (if available) 
- Abstract (the full abstract text if found)

If any field is unreadable or not found, return "unknown" for that field.

Return ONLY a raw JSON object with these exact field names: title, authors, year, journal, doi, keywords, abstract. Do not include any other text or markdown formatting."""

    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 3) -> str:
        """Extract text from the first few pages of a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = min(len(pdf_reader.pages), max_pages)
                text = ""
                
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n\n"
                    except Exception as e:
                        print(f"Error extracting text from page {page_num}: {str(e)}")
                        continue
                
                return text.strip()
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return ""

    def get_default_metadata(self) -> Dict:
        """Return default metadata structure with unknown values."""
        return {
            "title": "unknown",
            "authors": ["unknown"],
            "year": "unknown",
            "journal": "unknown",
            "doi": "unknown",
            "keywords": [],
            "abstract": "unknown"
        }

    def extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract metadata from paper text using Groq."""
        if not text:
            return self.get_default_metadata()

        max_retries = 3
        retry_delay = 2  # seconds
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Extract bibliographic information from this text:\n\n{text}"}
                    ],
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                
                # Try to parse as JSON first
                try:
                    metadata = json.loads(content)
                except json.JSONDecodeError:
                    # Fall back to text parsing
                    metadata = self.get_default_metadata()
                    
                    # Parse fields from text response
                    fields = {
                        "Title:": "title",
                        "Authors:": "authors",
                        "Year:": "year",
                        "Journal/Conference:": "journal",
                        "DOI:": "doi",
                        "Keywords:": "keywords",
                        "Abstract:": "abstract"
                    }
                    
                    for field_text, field_name in fields.items():
                        if field_text in content:
                            parts = content.split(field_text)
                            if len(parts) > 1:
                                field_content = parts[1].split("\n")[0].strip()
                                if field_name in ["authors", "keywords"]:
                                    items = [item.strip() for item in field_content.replace(";", ",").split(",")]
                                    metadata[field_name] = [item for item in items if item]
                                else:
                                    metadata[field_name] = field_content

                # Ensure all required fields exist
                default_metadata = self.get_default_metadata()
                for key in default_metadata:
                    if key not in metadata:
                        metadata[key] = default_metadata[key]
                
                return metadata
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Error extracting metadata: {str(e)}")
                    return self.get_default_metadata()

    def process_directory(self, directory_path: str) -> None:
        """Process all PDF files in a directory and save metadata."""
        results = []
        pdf_files = list(Path(directory_path).glob('*.pdf'))
        
        for pdf_path in pdf_files:
            print(f"\nProcessing {pdf_path.name}...")
            text = self.extract_text_from_pdf(str(pdf_path))
            
            metadata = self.extract_metadata(text)
            metadata['filename'] = pdf_path.name
            results.append(metadata)
            
            # Print extracted information
            print("\nExtracted Information:")
            print("-" * 50)
            print(f"Filename: {metadata['filename']}")
            print(f"Title: {metadata['title']}")
            print(f"Authors: {', '.join(metadata['authors']) if isinstance(metadata['authors'], list) else metadata['authors']}")
            print(f"Year: {metadata['year']}")
            print(f"Journal/Conference: {metadata['journal']}")
            print(f"DOI: {metadata['doi']}")
            print(f"Keywords: {', '.join(metadata['keywords']) if isinstance(metadata['keywords'], list) else metadata['keywords']}")
            print("\nAbstract:")
            print("-" * 50)
            print(metadata['abstract'])
            print("-" * 50)
            
            # Save intermediate results
            with open('metadata.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    # Get directory path from user
    directory = input("Enter the directory path containing PDF papers: ")
    
    # Initialize processor with Groq API key
    processor = PaperProcessor("GROQ-API_KEY")
    
    # Process all papers
    processor.process_directory(directory)
    print("\nProcessing complete. Results saved to paper_metadata.json")

if __name__ == "__main__":
    main()