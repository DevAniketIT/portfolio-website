#!/usr/bin/env python3
"""
Universal Web Scraper
A flexible web scraping tool for various websites with multiple output formats.
Perfect for Fiverr gigs ranging from ₹1500-3000.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import csv
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import argparse
import os
from datetime import datetime

class UniversalScraper:
    def __init__(self, delay: float = 1.0):
        """
        Initialize the scraper with configurable delay between requests
        """
        self.session = requests.Session()
        self.delay = delay
        self.setup_logging()
        
        # Headers to appear more like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'scraping_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info(f"Successfully scraped: {url}")
            
            time.sleep(self.delay)  # Be respectful to the server
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
    
    def extract_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict:
        """
        Extract data using CSS selectors
        
        Args:
            soup: BeautifulSoup object
            selectors: Dictionary mapping field names to CSS selectors
        """
        data = {}
        
        for field, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if len(elements) == 1:
                    data[field] = elements[0].get_text(strip=True)
                elif len(elements) > 1:
                    data[field] = [elem.get_text(strip=True) for elem in elements]
                else:
                    data[field] = None
                    
            except Exception as e:
                self.logger.warning(f"Error extracting {field}: {e}")
                data[field] = None
        
        return data
    
    def scrape_urls(self, urls: List[str], selectors: Dict[str, str]) -> List[Dict]:
        """
        Scrape multiple URLs with the same selectors
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{len(urls)}: {url}")
            
            soup = self.get_page(url)
            if soup:
                data = self.extract_data(soup, selectors)
                data['url'] = url
                data['scraped_at'] = datetime.now().isoformat()
                results.append(data)
        
        return results
    
    def save_results(self, data: List[Dict], output_file: str, format_type: str = 'csv'):
        """
        Save results in various formats
        """
        if not data:
            self.logger.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        
        if format_type.lower() == 'csv':
            df.to_csv(output_file, index=False, encoding='utf-8')
        elif format_type.lower() == 'excel':
            df.to_excel(output_file, index=False, engine='openpyxl')
        elif format_type.lower() == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")
    
    def scrape_ecommerce_products(self, base_url: str, max_pages: int = 5) -> List[Dict]:
        """
        Specialized method for scraping e-commerce product listings
        """
        products = []
        
        # Common e-commerce selectors (adjust based on target site)
        selectors = {
            'title': '.product-title, .product-name, h2, h3',
            'price': '.price, .product-price, .cost',
            'rating': '.rating, .stars, .review-score',
            'availability': '.stock, .availability',
            'image': 'img'
        }
        
        for page in range(1, max_pages + 1):
            page_url = f"{base_url}?page={page}"
            soup = self.get_page(page_url)
            
            if not soup:
                continue
            
            # Extract product links
            product_links = soup.select('a[href*="product"], a[href*="item"]')
            
            for link in product_links[:10]:  # Limit per page
                product_url = urljoin(base_url, link.get('href'))
                product_soup = self.get_page(product_url)
                
                if product_soup:
                    product_data = self.extract_data(product_soup, selectors)
                    product_data['url'] = product_url
                    products.append(product_data)
        
        return products
    
    def scrape_contact_info(self, urls: List[str]) -> List[Dict]:
        """
        Extract contact information from websites
        """
        contact_selectors = {
            'email': '[href^="mailto:"], .email',
            'phone': '[href^="tel:"], .phone',
            'address': '.address, .location',
            'company_name': 'h1, .company-name, .brand'
        }
        
        return self.scrape_urls(urls, contact_selectors)

def main():
    parser = argparse.ArgumentParser(description='Universal Web Scraper')
    parser.add_argument('--urls', nargs='+', required=True, help='URLs to scrape')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--format', choices=['csv', 'excel', 'json'], default='csv', help='Output format')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--selectors', help='JSON file with CSS selectors')
    
    args = parser.parse_args()
    
    # Load selectors
    if args.selectors and os.path.exists(args.selectors):
        with open(args.selectors, 'r') as f:
            selectors = json.load(f)
    else:
        # Default selectors
        selectors = {
            'title': 'title, h1, h2',
            'description': 'meta[name="description"]',
            'text_content': 'p, .content, .description'
        }
    
    # Initialize scraper
    scraper = UniversalScraper(delay=args.delay)
    
    # Scrape data
    results = scraper.scrape_urls(args.urls, selectors)
    
    # Save results
    scraper.save_results(results, args.output, args.format)
    
    print(f"Scraping completed! Results saved to {args.output}")

if __name__ == "__main__":
    main()
