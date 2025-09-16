"""
Scraping Service for Continuous Data Refresh
Handles web scraping from CraneTrader, CraneNetwork, and other marketplaces
"""

import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service for scraping crane listings from various marketplaces
    Implements polite scraping with rate limiting and caching
    """
    
    def __init__(self, cache_dir: Path = Path("data/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.rate_limit_delay = 2.0  # seconds between requests
        self.max_requests_per_minute = 30
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Marketplace configurations
        self.marketplaces = {
            'cranetrader': {
                'base_url': 'https://www.cranetrader.com',
                'search_url': 'https://www.cranetrader.com/listings/search',
                'rate_limit': 2.0,
                'max_pages': 50
            },
            'cranenetwork': {
                'base_url': 'https://www.cranenetwork.com',
                'search_url': 'https://www.cranenetwork.com/equipment/search',
                'rate_limit': 2.5,
                'max_pages': 30
            },
            'machinerytrader': {
                'base_url': 'https://www.machinerytrader.com',
                'search_url': 'https://www.machinerytrader.com/listings/search',
                'rate_limit': 3.0,
                'max_pages': 40
            }
        }
        
        # Request tracking
        self.request_count = 0
        self.last_request_time = 0
    
    async def scrape_all_marketplaces(self) -> Dict[str, Any]:
        """
        Scrape all configured marketplaces
        Returns summary of scraping results
        """
        try:
            results = {
                'total_listings': 0,
                'marketplaces_scraped': [],
                'errors': [],
                'start_time': datetime.utcnow().isoformat()
            }
            
            # Scrape each marketplace
            for marketplace_name, config in self.marketplaces.items():
                try:
                    marketplace_result = await self._scrape_marketplace(marketplace_name, config)
                    results['marketplaces_scraped'].append(marketplace_result)
                    results['total_listings'] += marketplace_result.get('listings_found', 0)
                except Exception as e:
                    error_msg = f"Error scraping {marketplace_name}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            results['end_time'] = datetime.utcnow().isoformat()
            results['duration_seconds'] = (
                datetime.fromisoformat(results['end_time']) - 
                datetime.fromisoformat(results['start_time'])
            ).total_seconds()
            
            logger.info(f"Scraping completed: {results['total_listings']} total listings found")
            return results
            
        except Exception as e:
            logger.error(f"Error in scraping service: {e}")
            raise
    
    async def _scrape_marketplace(self, marketplace_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape a specific marketplace"""
        try:
            listings = []
            page = 1
            max_pages = config.get('max_pages', 20)
            
            while page <= max_pages:
                try:
                    # Rate limiting
                    await self._rate_limit()
                    
                    # Scrape page
                    page_listings = await self._scrape_page(marketplace_name, config, page)
                    
                    if not page_listings:
                        logger.info(f"No more listings found on page {page} for {marketplace_name}")
                        break
                    
                    listings.extend(page_listings)
                    logger.info(f"Scraped page {page} of {marketplace_name}: {len(page_listings)} listings")
                    
                    page += 1
                    
                except Exception as e:
                    logger.warning(f"Error scraping page {page} of {marketplace_name}: {e}")
                    break
            
            return {
                'marketplace': marketplace_name,
                'listings_found': len(listings),
                'pages_scraped': page - 1,
                'listings': listings,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping {marketplace_name}: {e}")
            return {
                'marketplace': marketplace_name,
                'listings_found': 0,
                'pages_scraped': 0,
                'listings': [],
                'success': False,
                'error': str(e)
            }
    
    async def _scrape_page(self, marketplace_name: str, config: Dict[str, Any], page: int) -> List[Dict[str, Any]]:
        """Scrape a single page of listings"""
        try:
            # Build search URL with pagination
            search_url = self._build_search_url(config, page)
            
            # Check cache first
            cached_data = self._get_cached_data(search_url)
            if cached_data:
                return cached_data
            
            # Make request
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                async with session.get(search_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        listings = self._parse_listings(html, marketplace_name)
                        
                        # Cache the results
                        self._cache_data(search_url, listings)
                        
                        return listings
                    else:
                        logger.warning(f"HTTP {response.status} for {search_url}")
                        return []
        
        except Exception as e:
            logger.error(f"Error scraping page {page} of {marketplace_name}: {e}")
            return []
    
    def _build_search_url(self, config: Dict[str, Any], page: int) -> str:
        """Build search URL with pagination and filters"""
        base_url = config['search_url']
        
        # Add pagination
        if '?' in base_url:
            return f"{base_url}&page={page}"
        else:
            return f"{base_url}?page={page}"
    
    def _parse_listings(self, html: str, marketplace_name: str) -> List[Dict[str, Any]]:
        """Parse listings from HTML based on marketplace"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            if marketplace_name == 'cranetrader':
                return self._parse_cranetrader_listings(soup)
            elif marketplace_name == 'cranenetwork':
                return self._parse_cranenetwork_listings(soup)
            elif marketplace_name == 'machinerytrader':
                return self._parse_machinerytrader_listings(soup)
            else:
                return self._parse_generic_listings(soup, marketplace_name)
                
        except Exception as e:
            logger.error(f"Error parsing listings for {marketplace_name}: {e}")
            return []
    
    def _parse_cranetrader_listings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse CraneTrader listings"""
        listings = []
        
        # Look for listing containers (adjust selectors based on actual HTML)
        listing_containers = soup.find_all('div', class_=re.compile(r'listing|item|card'))
        
        for container in listing_containers:
            try:
                listing = self._extract_listing_data(container, 'cranetrader')
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Error parsing CraneTrader listing: {e}")
                continue
        
        return listings
    
    def _parse_cranenetwork_listings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse CraneNetwork listings"""
        listings = []
        
        # Look for listing containers
        listing_containers = soup.find_all('div', class_=re.compile(r'listing|item|card'))
        
        for container in listing_containers:
            try:
                listing = self._extract_listing_data(container, 'cranenetwork')
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Error parsing CraneNetwork listing: {e}")
                continue
        
        return listings
    
    def _parse_machinerytrader_listings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse MachineryTrader listings"""
        listings = []
        
        # Look for listing containers
        listing_containers = soup.find_all('div', class_=re.compile(r'listing|item|card'))
        
        for container in listing_containers:
            try:
                listing = self._extract_listing_data(container, 'machinerytrader')
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Error parsing MachineryTrader listing: {e}")
                continue
        
        return listings
    
    def _parse_generic_listings(self, soup: BeautifulSoup, marketplace_name: str) -> List[Dict[str, Any]]:
        """Parse listings using generic selectors"""
        listings = []
        
        # Generic selectors for common listing patterns
        listing_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'listing|item|card|result'))
        
        for container in listing_containers:
            try:
                listing = self._extract_listing_data(container, marketplace_name)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Error parsing generic listing: {e}")
                continue
        
        return listings
    
    def _extract_listing_data(self, container, marketplace_name: str) -> Optional[Dict[str, Any]]:
        """Extract listing data from a container element"""
        try:
            # Extract title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|name|heading'))
            if not title_elem:
                title_elem = container.find('a', class_=re.compile(r'title|name|heading'))
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract price
            price_elem = container.find(['span', 'div'], class_=re.compile(r'price|cost|amount'))
            if not price_elem:
                price_elem = container.find(text=re.compile(r'\$[\d,]+'))
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            price = self._extract_price(price_text)
            
            # Extract location
            location_elem = container.find(['span', 'div'], class_=re.compile(r'location|place|address'))
            if not location_elem:
                location_elem = container.find(text=re.compile(r'[A-Z][a-z]+,\s*[A-Z]{2}'))
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Extract year and manufacturer from title
            year = self._extract_year_from_title(title)
            manufacturer = self._extract_manufacturer_from_title(title)
            
            # Extract capacity
            capacity = self._extract_capacity_from_title(title)
            
            # Extract hours
            hours_elem = container.find(['span', 'div'], class_=re.compile(r'hours|hrs'))
            if not hours_elem:
                hours_elem = container.find(text=re.compile(r'\d+[\s,]*hours?'))
            hours_text = hours_elem.get_text(strip=True) if hours_elem else ''
            hours = self._extract_hours(hours_text)
            
            # Extract link
            link_elem = container.find('a', href=True)
            link = urljoin(self.marketplaces[marketplace_name]['base_url'], link_elem['href']) if link_elem else ''
            
            if not title or not price:
                return None
            
            listing = {
                'title': title,
                'manufacturer': manufacturer,
                'year': year,
                'price': price,
                'location': location,
                'hours': hours,
                'capacity_tons': capacity,
                'source': marketplace_name,
                'url': link,
                'scraped_at': datetime.utcnow().isoformat(),
                'raw_html': str(container)[:1000]  # Store first 1000 chars for debugging
            }
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting listing data: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> float:
        """Extract price from text"""
        if not price_text:
            return 0.0
        
        # Remove common price prefixes and suffixes
        price_text = re.sub(r'[^\d,.]', '', price_text)
        price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_year_from_title(self, title: str) -> int:
        """Extract year from title"""
        if not title:
            return 0
        
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        if year_match:
            try:
                return int(year_match.group())
            except (ValueError, TypeError):
                pass
        
        return 0
    
    def _extract_manufacturer_from_title(self, title: str) -> str:
        """Extract manufacturer from title"""
        if not title:
            return 'Unknown'
        
        # Common manufacturers
        manufacturers = [
            'Grove', 'Liebherr', 'Terex', 'Demag', 'Kato', 'Tadano',
            'Link-Belt', 'Manitowoc', 'Kobelco', 'Sany', 'XCMG'
        ]
        
        for manufacturer in manufacturers:
            if manufacturer.lower() in title.lower():
                return manufacturer
        
        return 'Unknown'
    
    def _extract_capacity_from_title(self, title: str) -> Optional[float]:
        """Extract capacity from title"""
        if not title:
            return None
        
        # Look for capacity patterns
        capacity_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)\b',
            r'(\d{3,4})\s*(?:t|ton|tons?)\b',
            r'(\d{3,4})\b'  # Fallback for 3-4 digit numbers
        ]
        
        for pattern in capacity_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    capacity = float(match.group(1))
                    if 10 <= capacity <= 2000:  # Reasonable capacity range
                        return capacity
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_hours(self, hours_text: str) -> int:
        """Extract hours from text"""
        if not hours_text:
            return 0
        
        hours_match = re.search(r'(\d+(?:,\d{3})*)', hours_text)
        if hours_match:
            try:
                return int(hours_match.group(1).replace(',', ''))
            except (ValueError, TypeError):
                pass
        
        return 0
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last_request)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _get_cached_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached data for URL"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{url_hash}.json"
            
            if cache_file.exists():
                # Check if cache is less than 1 hour old
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < 3600:  # 1 hour
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            return None
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def _cache_data(self, url: str, data: List[Dict[str, Any]]) -> None:
        """Cache data for URL"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{url_hash}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error caching data: {e}")
    
    def save_scraped_data(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Save scraped data to JSONL file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for record in data:
                    f.write(json.dumps(record) + '\n')
            logger.info(f"Scraped data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
            raise
