import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Setup Selenium WebDriver
CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"  # Update with the correct ChromeDriver path
options = Options()
options.add_argument("--headless")  # Run in headless mode (no UI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Define main Changi Airport URL
MAIN_URL = "https://www.changiairport.com/"
driver.get(MAIN_URL)
time.sleep(3)  # Allow page to load

# Dictionary to store scraped data
scraped_data = {}

# Function to extract all links from a page
def extract_links():
    """Extracts all unique links from the current page."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = {
        a.text.strip(): a["href"]
        for a in soup.find_all("a", href=True)
        if "changiairport.com" in a["href"]  # Ensure it's an internal link
    }
    return links

# Function to scrape a page
def scrape_page(category, page_name, page_url, is_main_page=False):
    """Scrapes a page and extracts content. Only scrapes sublinks if it's the main page."""
    
    print(f"🔗 Scraping: {page_name} ({page_url})")

    driver.get(page_url)
    time.sleep(3)  # Allow page to load

    # Parse page content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract content
    headings = [h.text.strip() for h in soup.find_all("h1")]
    sub_headings = [h.text.strip() for h in soup.find_all("h2")]
    paragraphs = [p.text.strip() for p in soup.find_all("p")]
    
    # Store scraped data
    scraped_data[category] = {
        "page_url": page_url,
        "headings": headings,
        "sub_headings": sub_headings,
        "paragraphs": paragraphs
    }

    # Only extract links **if this is the main page**
    if is_main_page:
        sublinks = extract_links()
        scraped_data[category]["sublinks"] = sublinks  # Store only at the main page level

# Extract main navbar links (only from the main page)
main_nav_links = extract_links()

# Step 1: Scrape all main navbar pages
for category, url in main_nav_links.items():
    if "changiairport.com" in url:  # Ensure it's an internal link
        scrape_page(category, category, url, is_main_page=True)

# Close WebDriver
driver.quit()

# Save scraped data to JSON
with open("changi_airport_full_data.json", "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, indent=4, ensure_ascii=False)

print("✅ Scraping complete! Data saved to 'changi_airport_full_data.json'")
