import os
import json
import glob
from bs4 import BeautifulSoup

def clean_html(soup):
    # Remove noisy tags
    for tag in soup(['nav', 'footer', 'header', 'script', 'style', 'aside', 'svg']):
        tag.decompose()
    return soup

def extract_section(soup, keywords):
    # Heuristic: find headers or divs that contain our keywords
    for keyword in keywords:
        elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
        for el in elements:
            # Get parent to extract context
            parent = el.parent
            # Find the next sibling or parent's sibling to get the value
            # Since Groww often uses tables or flex divs, we grab the parent's text or parent's parent text
            for i in range(4): # Go up a few levels to capture the whole block
                if parent:
                    text = parent.get_text(separator=" ", strip=True)
                    if len(text) > len(keyword) + 10: # Ensure we captured more than just the header
                        return text
                    parent = parent.parent
    return None

def parse_files():
    # Find the most recent raw directory
    raw_dirs = sorted(glob.glob(os.path.join("data", "raw", "*")))
    if not raw_dirs:
        print("No raw data found.")
        return
    
    latest_raw_dir = raw_dirs[-1]
    parsed_dir = os.path.join("data", "parsed")
    os.makedirs(parsed_dir, exist_ok=True)
    
    print(f"Parsing files from {latest_raw_dir}")
    
    for file_path in glob.glob(os.path.join(latest_raw_dir, "*.html")):
        filename = os.path.basename(file_path)
        fund_name = filename.replace(".html", "")
        print(f"Parsing: {fund_name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        soup = clean_html(soup)
        
        # Extract fields
        data = {
            "fund_name": fund_name,
            "overview": extract_section(soup, ["about this fund", "fund details"]),
            "expense_ratio": extract_section(soup, ["expense ratio", "ter "]),
            "exit_load": extract_section(soup, ["exit load"]),
            "minimum_investment": extract_section(soup, ["minimum sip", "minimum investment", "min investment"]),
            "benchmark": extract_section(soup, ["benchmark", "index"]),
            "tax": extract_section(soup, ["tax implications", "taxability", "tax returns"]),
            "fund_management": extract_section(soup, ["fund manager", "management"]),
            "investment_objective": extract_section(soup, ["investment objective", "objective"]),
            "fund_house": extract_section(soup, ["fund house", "amc details"])
        }
        
        out_file = os.path.join(parsed_dir, f"{fund_name}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"  -> Saved to {out_file}")

if __name__ == "__main__":
    parse_files()
