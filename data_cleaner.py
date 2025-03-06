import json
import re
from typing import List, Dict
from pathlib import Path

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?\-&\'"/]', '', text)
    # Replace common HTML entities
    return text.replace('&nbsp;', ' ').replace('&amp;', '&')

def process_paragraphs(paragraphs: List[str]) -> List[str]:
    """Clean and deduplicate paragraphs with context-aware merging"""
    cleaned = []
    seen = set()
    
    for p in paragraphs:
        cleaned_p = clean_text(p)
        if not cleaned_p:
            continue
            
        # Merge short consecutive items
        if cleaned and len(cleaned[-1]) < 80 and len(cleaned_p) < 80:
            cleaned[-1] += " " + cleaned_p
        elif cleaned_p not in seen:
            cleaned.append(cleaned_p)
            seen.add(cleaned_p)
    
    return cleaned

def clean_changi_data(input_file: Path, output_file: Path):
    """Main cleaning pipeline with sublink removal"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    for page_key, page_data in data.items():
        cleaned_page = {
            "page_url": clean_text(page_data.get("page_url", "")),
            "paragraphs": process_paragraphs(page_data.get("paragraphs", []))
        }
        
        # Remove empty pages
        if cleaned_page["page_url"] and cleaned_page["paragraphs"]:
            cleaned_data[page_key] = cleaned_page
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_path = Path("data/changi_airport_full_data.json")
    output_path = Path("data/changi_airport_full_data_cleaned.json")
    
    clean_changi_data(input_path, output_path)
    print(f"✅ Cleaned data saved to {output_path}")
