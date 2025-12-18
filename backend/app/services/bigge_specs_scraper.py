"""
Bigge Equipment Specification Catalog Scraper
Scrapes crane specifications from Bigge's database for accurate comparisons
"""

import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import hashlib
import re
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pdfplumber
import requests

logger = logging.getLogger(__name__)

class BiggeSpecsScraper:
    """
    Scraper for Bigge Equipment's specification catalog
    Extracts detailed crane specifications for accurate comparisons
    """
    
    def __init__(self, cache_dir: Path = Path("data/cache/bigge"), output_dir: Path = Path("data/raw/specs")):
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Bigge Equipment base URLs
        self.base_url = "https://www.bigge.com"
        self.categories_url = "https://www.bigge.com/equipment/cranes"
        self.specs_url = "https://www.bigge.com/equipment/cranes/specifications"
        
        # Rate limiting
        self.rate_limit_delay = 3.0  # seconds between requests
        self.max_requests_per_minute = 20
        
        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Crane categories to scrape
        self.crane_categories = [
            'all-terrain-cranes',
            'crawler-cranes', 
            'rough-terrain-cranes',
            'truck-cranes',
            'tower-cranes',
            'boom-trucks'
        ]
        
        # Specification patterns
        self.spec_patterns = {
            'capacity': [
                r'(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)\b',
                r'capacity[:\s]*(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)',
                r'max[imum]?\s*load[:\s]*(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)'
            ],
            'boom_length': [
                r'boom[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'main\s*boom[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)\s*boom'
            ],
            'jib_length': [
                r'jib[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'fly\s*jib[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)\s*jib'
            ],
            'counterweight': [
                r'counterweight[:\s]*(\d+(?:,\d{3})*)\s*(?:lb|lbs|kg)',
                r'ballast[:\s]*(\d+(?:,\d{3})*)\s*(?:lb|lbs|kg)',
                r'(\d+(?:,\d{3})*)\s*(?:lb|lbs|kg)\s*counterweight'
            ],
            'engine': [
                r'engine[:\s]*([A-Za-z0-9\s\-\.]+)',
                r'power[:\s]*([A-Za-z0-9\s\-\.]+)',
                r'motor[:\s]*([A-Za-z0-9\s\-\.]+)'
            ],
            'dimensions': [
                r'length[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'width[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)',
                r'height[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)'
            ]
        }
        
        # Request tracking
        self.request_count = 0
        self.last_request_time = 0
        self.scraped_specs = []
    
    async def scrape_all_specifications(self) -> Dict[str, Any]:
        """
        Scrape all crane specifications from Bigge's catalog
        """
        try:
            logger.info("Starting Bigge specifications scraping...")
            start_time = datetime.utcnow()
            
            results = {
                'total_specs': 0,
                'categories_scraped': [],
                'errors': [],
                'start_time': start_time.isoformat()
            }
            
            # Scrape each category
            for category in self.crane_categories:
                try:
                    category_result = await self._scrape_category(category)
                    results['categories_scraped'].append(category_result)
                    results['total_specs'] += category_result.get('specs_found', 0)
                except Exception as e:
                    error_msg = f"Error scraping category {category}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Save all specifications
            output_file = self.output_dir / f"bigge_specs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
            self._save_specifications(output_file)
            
            results['end_time'] = datetime.utcnow().isoformat()
            results['duration_seconds'] = (datetime.fromisoformat(results['end_time']) - start_time).total_seconds()
            results['output_file'] = str(output_file)
            
            logger.info(f"Bigge specifications scraping completed: {results['total_specs']} specs found")
            return results
            
        except Exception as e:
            logger.error(f"Error in Bigge specifications scraping: {e}")
            raise
    
    async def _scrape_category(self, category: str) -> Dict[str, Any]:
        """Scrape specifications for a specific crane category"""
        try:
            category_url = f"{self.categories_url}/{category}"
            logger.info(f"Scraping category: {category}")
            
            # Get category page
            category_page = await self._get_page(category_url)
            if not category_page:
                return {'category': category, 'specs_found': 0, 'error': 'Failed to load category page'}
            
            # Parse category page for model links
            model_links = self._extract_model_links(category_page, category)
            logger.info(f"Found {len(model_links)} models in {category}")
            
            specs_found = 0
            for model_link in model_links:
                try:
                    # Rate limiting
                    await self._rate_limit()
                    
                    # Scrape model specifications
                    model_specs = await self._scrape_model_specifications(model_link, category)
                    if model_specs:
                        self.scraped_specs.append(model_specs)
                        specs_found += 1
                        logger.info(f"Scraped specs for {model_specs.get('model', 'Unknown')}")
                    
                except Exception as e:
                    logger.warning(f"Error scraping model {model_link}: {e}")
                    continue
            
            return {
                'category': category,
                'specs_found': specs_found,
                'models_processed': len(model_links),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping category {category}: {e}")
            return {'category': category, 'specs_found': 0, 'error': str(e)}
    
    def _extract_model_links(self, html: str, category: str) -> List[str]:
        """Extract model links from category page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            model_links = []
            
            # Look for model links (adjust selectors based on actual HTML)
            link_selectors = [
                'a[href*="/equipment/cranes/"]',
                'a[href*="/cranes/"]',
                'a[href*="/specifications/"]',
                '.model-link',
                '.crane-model',
                '.equipment-item a'
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and self._is_model_link(href, category):
                        full_url = urljoin(self.base_url, href)
                        model_links.append(full_url)
            
            # Remove duplicates
            return list(set(model_links))
            
        except Exception as e:
            logger.error(f"Error extracting model links: {e}")
            return []
    
    def _is_model_link(self, href: str, category: str) -> bool:
        """Check if link is a model specification page"""
        if not href:
            return False
        
        # Skip non-model links
        skip_patterns = [
            '/contact', '/about', '/news', '/careers', '/support',
            '/rental', '/sales', '/parts', '/service'
        ]
        
        for pattern in skip_patterns:
            if pattern in href.lower():
                return False
        
        # Look for model indicators
        model_indicators = [
            '/equipment/cranes/',
            '/cranes/',
            '/specifications/',
            category.replace('-', '')
        ]
        
        return any(indicator in href.lower() for indicator in model_indicators)
    
    async def _scrape_model_specifications(self, model_url: str, category: str) -> Optional[Dict[str, Any]]:
        """Scrape specifications for a specific model"""
        try:
            # Get model page
            model_page = await self._get_page(model_url)
            if not model_page:
                return None
            
            # Parse specifications
            specs = self._parse_specifications(model_page, model_url, category)
            if not specs:
                return None
            
            # Try to get PDF specifications if available
            pdf_specs = await self._extract_pdf_specifications(model_page, model_url)
            if pdf_specs:
                specs['pdf_specifications'] = pdf_specs
            
            return specs
            
        except Exception as e:
            logger.warning(f"Error scraping model specifications from {model_url}: {e}")
            return None
    
    def _parse_specifications(self, html: str, url: str, category: str) -> Optional[Dict[str, Any]]:
        """Parse specifications from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract basic model information
            model_info = self._extract_model_info(soup, url)
            if not model_info:
                return None
            
            # Extract specifications
            specifications = self._extract_specifications_from_html(soup)
            
            # Extract features
            features = self._extract_features(soup)
            
            # Extract dimensions
            dimensions = self._extract_dimensions(soup)
            
            # Create specification record
            spec_record = {
                'spec_id': self._generate_spec_id(model_info, url),
                'source': 'bigge',
                'source_url': url,
                'last_seen': datetime.utcnow().isoformat(),
                'category': category,
                'make': model_info.get('make', 'Bigge'),
                'model': model_info.get('model', 'Unknown'),
                'variant': model_info.get('variant', 'Standard'),
                'year_from': model_info.get('year_from'),
                'year_to': model_info.get('year_to'),
                'capacity_tons': specifications.get('capacity'),
                'boom_length_ft': specifications.get('boom_length'),
                'jib_options_ft': specifications.get('jib_options', []),
                'counterweight_lbs': specifications.get('counterweight'),
                'engine': specifications.get('engine'),
                'dimensions': dimensions,
                'features': features,
                'pdf_specs': specifications.get('pdf_specs', []),
                'raw_html': html[:2000],  # Store first 2000 chars for debugging
                'spec_hash': self._generate_spec_hash(model_info, specifications)
            }
            
            return spec_record
            
        except Exception as e:
            logger.error(f"Error parsing specifications: {e}")
            return None
    
    def _extract_model_info(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extract basic model information"""
        try:
            # Extract title
            title_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading|model'))
            if not title_elem:
                title_elem = soup.find('title')
            
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract make and model from title
            make, model = self._parse_make_model(title)
            
            # Extract year range if available
            year_from, year_to = self._extract_year_range(soup)
            
            return {
                'title': title,
                'make': make,
                'model': model,
                'year_from': year_from,
                'year_to': year_to
            }
            
        except Exception as e:
            logger.error(f"Error extracting model info: {e}")
            return None
    
    def _parse_make_model(self, title: str) -> Tuple[str, str]:
        """Parse make and model from title"""
        if not title:
            return 'Bigge', 'Unknown'
        
        # Common patterns
        patterns = [
            r'(\w+)\s+(\w+\d+)',  # "Grove GMK5250L"
            r'(\w+)\s+([A-Z]+\d+)',  # "Liebherr LTM1500"
            r'(\w+)\s+([A-Z]+\d+[A-Z]*)',  # "Terex AC500"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).title(), match.group(2)
        
        # Fallback
        words = title.split()
        if len(words) >= 2:
            return words[0].title(), ' '.join(words[1:])
        
        return 'Bigge', title
    
    def _extract_year_range(self, soup: BeautifulSoup) -> Tuple[Optional[int], Optional[int]]:
        """Extract year range from page"""
        try:
            # Look for year information in various places
            year_text = ''
            
            # Check title
            title_elem = soup.find(['h1', 'h2', 'h3'])
            if title_elem:
                year_text += title_elem.get_text() + ' '
            
            # Check specification tables
            spec_tables = soup.find_all('table')
            for table in spec_tables:
                year_text += table.get_text() + ' '
            
            # Extract years
            years = re.findall(r'\b(19|20)\d{2}\b', year_text)
            if years:
                years = [int(year) for year in years]
                return min(years), max(years)
            
            return None, None
            
        except Exception as e:
            logger.warning(f"Error extracting year range: {e}")
            return None, None
    
    def _extract_specifications_from_html(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract specifications from HTML tables and text"""
        try:
            specifications = {}
            
            # Extract from specification tables
            spec_tables = soup.find_all('table')
            for table in spec_tables:
                self._parse_specification_table(table, specifications)
            
            # Extract from text content
            text_content = soup.get_text()
            self._parse_specification_text(text_content, specifications)
            
            return specifications
            
        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")
            return {}
    
    def _parse_specification_table(self, table, specifications: Dict[str, Any]):
        """Parse specifications from HTML table"""
        try:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Parse different specification types
                    if 'capacity' in label or 'load' in label:
                        capacity = self._extract_capacity(value)
                        if capacity:
                            specifications['capacity'] = capacity
                    
                    elif 'boom' in label:
                        boom_length = self._extract_length(value)
                        if boom_length:
                            specifications['boom_length'] = boom_length
                    
                    elif 'jib' in label:
                        jib_length = self._extract_length(value)
                        if jib_length:
                            if 'jib_options' not in specifications:
                                specifications['jib_options'] = []
                            specifications['jib_options'].append(jib_length)
                    
                    elif 'counterweight' in label or 'ballast' in label:
                        counterweight = self._extract_weight(value)
                        if counterweight:
                            specifications['counterweight'] = counterweight
                    
                    elif 'engine' in label or 'power' in label:
                        engine = value.strip()
                        if engine and len(engine) > 2:
                            specifications['engine'] = engine
                    
                    elif 'dimension' in label or 'size' in label:
                        dimensions = self._extract_dimensions_from_text(value)
                        if dimensions:
                            specifications.update(dimensions)
            
        except Exception as e:
            logger.warning(f"Error parsing specification table: {e}")
    
    def _parse_specification_text(self, text: str, specifications: Dict[str, Any]):
        """Parse specifications from text content"""
        try:
            # Extract capacity
            if 'capacity' not in specifications:
                capacity = self._extract_capacity(text)
                if capacity:
                    specifications['capacity'] = capacity
            
            # Extract boom length
            if 'boom_length' not in specifications:
                boom_length = self._extract_boom_length(text)
                if boom_length:
                    specifications['boom_length'] = boom_length
            
            # Extract jib options
            if 'jib_options' not in specifications:
                jib_options = self._extract_jib_options(text)
                if jib_options:
                    specifications['jib_options'] = jib_options
            
            # Extract counterweight
            if 'counterweight' not in specifications:
                counterweight = self._extract_counterweight(text)
                if counterweight:
                    specifications['counterweight'] = counterweight
            
            # Extract engine
            if 'engine' not in specifications:
                engine = self._extract_engine(text)
                if engine:
                    specifications['engine'] = engine
            
        except Exception as e:
            logger.warning(f"Error parsing specification text: {e}")
    
    def _extract_capacity(self, text: str) -> Optional[float]:
        """Extract capacity in tons"""
        for pattern in self.spec_patterns['capacity']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    capacity = float(match.group(1))
                    if 10 <= capacity <= 2000:  # Reasonable range
                        return capacity
                except (ValueError, TypeError):
                    continue
        return None
    
    def _extract_boom_length(self, text: str) -> Optional[float]:
        """Extract boom length in feet"""
        for pattern in self.spec_patterns['boom_length']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    length = float(match.group(1))
                    # Convert meters to feet if needed
                    if 'm' in text.lower() and 'meter' in text.lower():
                        length *= 3.28084
                    if 10 <= length <= 500:  # Reasonable range
                        return length
                except (ValueError, TypeError):
                    continue
        return None
    
    def _extract_jib_options(self, text: str) -> List[float]:
        """Extract jib options in feet"""
        jib_options = []
        for pattern in self.spec_patterns['jib_length']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    length = float(match)
                    # Convert meters to feet if needed
                    if 'm' in text.lower() and 'meter' in text.lower():
                        length *= 3.28084
                    if 10 <= length <= 200:  # Reasonable range
                        jib_options.append(length)
                except (ValueError, TypeError):
                    continue
        return sorted(list(set(jib_options)))
    
    def _extract_counterweight(self, text: str) -> Optional[int]:
        """Extract counterweight in pounds"""
        for pattern in self.spec_patterns['counterweight']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    weight_str = match.group(1).replace(',', '')
                    weight = int(weight_str)
                    # Convert kg to lbs if needed
                    if 'kg' in text.lower():
                        weight = int(weight * 2.20462)
                    if 1000 <= weight <= 500000:  # Reasonable range
                        return weight
                except (ValueError, TypeError):
                    continue
        return None
    
    def _extract_engine(self, text: str) -> Optional[str]:
        """Extract engine information"""
        for pattern in self.spec_patterns['engine']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                engine = match.group(1).strip()
                if len(engine) > 2 and len(engine) < 100:
                    return engine
        return None
    
    def _extract_length(self, text: str) -> Optional[float]:
        """Extract length value from text"""
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ft|feet|m|meter)', text, re.IGNORECASE)
        if match:
            try:
                length = float(match.group(1))
                if 'm' in text.lower() and 'meter' in text.lower():
                    length *= 3.28084
                return length
            except (ValueError, TypeError):
                pass
        return None
    
    def _extract_weight(self, text: str) -> Optional[int]:
        """Extract weight value from text"""
        match = re.search(r'(\d+(?:,\d{3})*)\s*(?:lb|lbs|kg)', text, re.IGNORECASE)
        if match:
            try:
                weight_str = match.group(1).replace(',', '')
                weight = int(weight_str)
                if 'kg' in text.lower():
                    weight = int(weight * 2.20462)
                return weight
            except (ValueError, TypeError):
                pass
        return None
    
    def _extract_dimensions_from_text(self, text: str) -> Dict[str, float]:
        """Extract dimensions from text"""
        dimensions = {}
        for dim_type in ['length', 'width', 'height']:
            pattern = f'{dim_type}[:\\s]*(\\d+(?:\\.\\d+)?)\\s*(?:ft|feet|m|meter)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    if 'm' in text.lower() and 'meter' in text.lower():
                        value *= 3.28084
                    dimensions[f'{dim_type}_ft'] = value
                except (ValueError, TypeError):
                    pass
        return dimensions
    
    def _extract_dimensions(self, soup: BeautifulSoup) -> Dict[str, float]:
        """Extract dimensions from page"""
        try:
            dimensions = {}
            text_content = soup.get_text()
            
            for dim_type in ['length', 'width', 'height']:
                pattern = f'{dim_type}[:\\s]*(\\d+(?:\\.\\d+)?)\\s*(?:ft|feet|m|meter)'
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        if 'm' in text_content.lower() and 'meter' in text_content.lower():
                            value *= 3.28084
                        dimensions[f'{dim_type}_ft'] = value
                    except (ValueError, TypeError):
                        pass
            
            return dimensions
            
        except Exception as e:
            logger.warning(f"Error extracting dimensions: {e}")
            return {}
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract features from page"""
        try:
            features = []
            
            # Look for feature lists
            feature_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'feature|spec|option'))
            for feature_list in feature_lists:
                items = feature_list.find_all('li')
                for item in items:
                    feature = item.get_text(strip=True)
                    if feature and len(feature) > 2:
                        features.append(feature)
            
            # Look for feature text
            feature_text = soup.find_all(text=re.compile(r'feature|option|equipment', re.IGNORECASE))
            for text in feature_text:
                if len(text.strip()) > 10 and len(text.strip()) < 200:
                    features.append(text.strip())
            
            return list(set(features))[:20]  # Limit to 20 features
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
            return []
    
    async def _extract_pdf_specifications(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Extract PDF specifications if available"""
        try:
            pdf_specs = []
            
            # Look for PDF links
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
            for link in pdf_links:
                pdf_url = urljoin(url, link['href'])
                pdf_text = await self._extract_pdf_text(pdf_url)
                if pdf_text:
                    pdf_specs.append({
                        'url': pdf_url,
                        'text': pdf_text[:5000],  # First 5000 chars
                        'extracted_at': datetime.utcnow().isoformat()
                    })
            
            return pdf_specs
            
        except Exception as e:
            logger.warning(f"Error extracting PDF specifications: {e}")
            return []
    
    async def _extract_pdf_text(self, pdf_url: str) -> Optional[str]:
        """Extract text from PDF"""
        try:
            # Check cache first
            pdf_hash = hashlib.md5(pdf_url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{pdf_hash}.txt"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Download PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, timeout=30) as response:
                    if response.status == 200:
                        pdf_content = await response.read()
                        
                        # Extract text using pdfplumber
                        import io
                        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
                            
                            # Cache the text
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            return text
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting PDF text from {pdf_url}: {e}")
            return None
    
    def _generate_spec_id(self, model_info: Dict[str, Any], url: str) -> str:
        """Generate unique specification ID"""
        make = model_info.get('make', 'Unknown')
        model = model_info.get('model', 'Unknown')
        return f"bigge_{make}_{model}_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def _generate_spec_hash(self, model_info: Dict[str, Any], specifications: Dict[str, Any]) -> str:
        """Generate specification hash for deduplication"""
        hash_string = f"{model_info.get('make', '')}|{model_info.get('model', '')}|{specifications.get('capacity', '')}|{specifications.get('boom_length', '')}"
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    async def _get_page(self, url: str) -> Optional[str]:
        """Get page content with caching"""
        try:
            # Check cache first
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{url_hash}.html"
            
            if cache_file.exists():
                # Check if cache is less than 24 hours old
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < 86400:  # 24 hours
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
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
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Cache the HTML
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            f.write(html)
                        
                        return html
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting page {url}: {e}")
            return None
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last_request)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _save_specifications(self, output_file: Path):
        """Save scraped specifications to JSONL file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for spec in self.scraped_specs:
                    f.write(json.dumps(spec) + '\n')
            logger.info(f"Specifications saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving specifications: {e}")
            raise
