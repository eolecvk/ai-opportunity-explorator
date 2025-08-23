import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page
import re
import urllib.parse
from datetime import datetime, timedelta

@dataclass
class ValidationResult:
    status: str  # 'valid', 'ambiguous', 'invalid'
    confidence: int  # 0-100
    message: str
    company_name: str
    suggestions: List[str]
    sources: List[str]  # Which validation sources were used
    details: Dict[str, Any]  # Additional validation details

class WebCompanyValidator:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)
        
        # User agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    async def __aenter__(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

    async def validate_company(self, company_name: str) -> ValidationResult:
        """Main validation method using multiple strategies"""
        
        # Check cache first
        cache_key = company_name.lower().strip()
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_result

        try:
            # Initialize validation result
            result = ValidationResult(
                status='invalid',
                confidence=0,
                message='',
                company_name=company_name,
                suggestions=[],
                sources=[],
                details={}
            )

            # Try direct domain validation first (fastest)
            direct_result = await self._try_direct_domain_validation(company_name)
            confidence_score = 0
            sources = []
            details = {}

            if direct_result['found']:
                confidence_score += 50
                sources.append('Direct Domain')
                details['direct_domain'] = direct_result

            # If direct domain found, try additional validations in parallel
            if confidence_score > 0:
                try:
                    # Run additional strategies with shorter timeout
                    strategies = [
                        self._search_linkedin_company(company_name),
                        self._search_wikipedia(company_name)
                    ]

                    results = await asyncio.wait_for(
                        asyncio.gather(*strategies, return_exceptions=True),
                        timeout=10.0
                    )

                    # LinkedIn validation
                    if results[0] and not isinstance(results[0], Exception):
                        linkedin_data = results[0]
                        if linkedin_data['found']:
                            confidence_score += 20
                            sources.append('LinkedIn')
                            details['linkedin'] = linkedin_data

                    # Wikipedia validation
                    if results[1] and not isinstance(results[1], Exception):
                        wikipedia_data = results[1]
                        if wikipedia_data['found']:
                            confidence_score += 15
                            sources.append('Wikipedia')
                            details['wikipedia'] = wikipedia_data

                except asyncio.TimeoutError:
                    logging.warning(f"Additional validation timeout for {company_name}")

            # Multiple sources bonus
            if len(sources) >= 2:
                confidence_score += 10

            # Determine final status and message
            result.confidence = min(confidence_score, 100)
            result.sources = sources
            result.details = details

            if confidence_score >= 80:
                result.status = 'valid'
                result.message = f"High confidence: {company_name} verified via {', '.join(sources)}"
            elif confidence_score >= 50:
                result.status = 'valid'
                result.message = f"Medium confidence: {company_name} found via {', '.join(sources)}"
            elif confidence_score >= 20:
                result.status = 'ambiguous'
                result.message = f"Low confidence: Limited information found for {company_name}"
            else:
                result.status = 'invalid'
                result.message = f"No reliable information found for '{company_name}'. Please verify the company name."

            # Cache the result
            self.cache[cache_key] = (result, datetime.now())
            
            return result

        except Exception as e:
            logging.error(f"Web validation error for {company_name}: {e}")
            return ValidationResult(
                status='invalid',
                confidence=0,
                message=f"Validation failed due to technical error",
                company_name=company_name,
                suggestions=[],
                sources=[],
                details={'error': str(e)}
            )
    
    async def _try_direct_domain_validation(self, company_name: str) -> Dict[str, Any]:
        """Try to validate by directly checking likely company domains"""
        if not self.browser:
            return {'found': False, 'error': 'Browser not initialized'}

        # Generate likely domain names
        company_clean = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        company_words = [word.lower() for word in company_name.split() if len(word) > 1]
        
        potential_domains = []
        
        # Direct company name
        potential_domains.extend([
            f"{company_clean}.com",
            f"{company_name.lower().replace(' ', '')}.com",
            f"{company_name.lower().replace(' ', '-')}.com"
        ])
        
        # Individual words for single-word companies
        if len(company_words) == 1:
            potential_domains.append(f"{company_words[0]}.com")
        
        # Acronyms for multi-word companies
        if len(company_words) > 1:
            acronym = ''.join([word[0] for word in company_words])
            potential_domains.append(f"{acronym}.com")
        
        # Try each potential domain
        for domain in potential_domains[:5]:  # Limit to first 5 attempts
            try:
                page = await self.browser.new_page()
                
                try:
                    response = await page.goto(f"https://{domain}", timeout=5000)
                    status = response.status if response else 0
                    
                    # Accept various status codes that indicate domain exists
                    if response and (status < 400 or status in [403, 429]):  # 403 = Forbidden, 429 = Rate Limited
                        
                        if status < 400:
                            # Page loaded successfully, check title
                            title = await page.title()
                            
                            # Check if title contains company name
                            title_lower = title.lower()
                            company_lower = company_name.lower()
                            
                            # Flexible matching for title validation
                            if (company_lower in title_lower or 
                                any(word in title_lower for word in company_words if len(word) > 2) or
                                company_clean in title_lower.replace(' ', '')):
                                
                                await page.close()
                                return {
                                    'found': True,
                                    'url': f"https://{domain}",
                                    'title': title,
                                    'domain': domain
                                }
                        else:
                            # Domain exists but is blocking us (403, 429)
                            # This is strong evidence the company exists
                            await page.close()
                            return {
                                'found': True,
                                'url': f"https://{domain}",
                                'title': f"{company_name} (Protected Domain)",
                                'domain': domain,
                                'status': status
                            }
                
                except Exception:
                    # Domain doesn't exist or is not accessible
                    pass
                finally:
                    await page.close()
                    
            except Exception as e:
                logging.debug(f"Error checking domain {domain}: {e}")
                continue
        
        return {'found': False}

    async def _search_official_website(self, company_name: str) -> Dict[str, Any]:
        """Search for official company website using DuckDuckGo (less restrictive)"""
        if not self.browser:
            return {'found': False, 'error': 'Browser not initialized'}

        try:
            page = await self.browser.new_page(
                user_agent=self.user_agents[0]
            )
            
            # Use DuckDuckGo instead of Google (less bot detection)
            search_query = f'"{company_name}" official website'
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(search_query)}"
            
            await page.goto(search_url, timeout=8000)
            
            # Wait for results to load
            try:
                await page.wait_for_selector('article[data-testid="result"]', timeout=5000)
            except:
                # Try alternate wait
                await asyncio.sleep(2)

            # Look for search results (DuckDuckGo structure)
            search_results = await page.query_selector_all('article[data-testid="result"]')
            
            if not search_results:
                # Fallback selectors for DuckDuckGo
                search_results = await page.query_selector_all('div.results_links')

            website_info = {'found': False}
            
            for result in search_results[:5]:  # Check first 5 results
                try:
                    # Get URL from DuckDuckGo result
                    link_element = await result.query_selector('a[data-testid="result-title-a"]')
                    if not link_element:
                        link_element = await result.query_selector('a')
                    
                    if link_element:
                        url = await link_element.get_attribute('href')
                        
                        # DuckDuckGo sometimes uses redirect URLs
                        if url and '/l/?uddg=' in url:
                            # Skip redirect URLs for now
                            continue
                            
                        if url and self._is_likely_official_domain(url, company_name):
                            # Get title
                            title_element = await result.query_selector('h2')
                            if not title_element:
                                title_element = await result.query_selector('a[data-testid="result-title-a"]')
                            
                            title = await title_element.inner_text() if title_element else ''
                            
                            website_info = {
                                'found': True,
                                'url': url,
                                'title': title.strip(),
                                'domain': self._extract_domain(url)
                            }
                            break
                except Exception as e:
                    logging.debug(f"Error processing search result: {e}")
                    continue

            await page.close()
            return website_info

        except Exception as e:
            logging.warning(f"Official website search failed for {company_name}: {e}")
            return {'found': False, 'error': str(e)}

    async def _search_linkedin_company(self, company_name: str) -> Dict[str, Any]:
        """Search for LinkedIn company page using direct search"""
        if not self.browser:
            return {'found': False, 'error': 'Browser not initialized'}

        try:
            page = await self.browser.new_page(
                user_agent=self.user_agents[1]
            )

            # Search DuckDuckGo for LinkedIn company pages
            search_query = f'site:linkedin.com/company "{company_name}"'
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(search_query)}"
            
            await page.goto(search_url, timeout=8000)
            await asyncio.sleep(2)  # Simple wait for results

            # Look for any links containing LinkedIn
            all_links = await page.query_selector_all('a')
            
            linkedin_info = {'found': False}
            
            for link in all_links[:10]:  # Check first 10 links
                try:
                    url = await link.get_attribute('href')
                    if url and 'linkedin.com/company' in url and company_name.lower().replace(' ', '') in url.lower():
                        title = await link.inner_text()
                        linkedin_info = {
                            'found': True,
                            'url': url,
                            'title': title.strip()
                        }
                        break
                except:
                    continue

            await page.close()
            return linkedin_info

        except Exception as e:
            logging.warning(f"LinkedIn search failed for {company_name}: {e}")
            return {'found': False, 'error': str(e)}

    async def _search_wikipedia(self, company_name: str) -> Dict[str, Any]:
        """Search for Wikipedia page using DuckDuckGo"""
        if not self.browser:
            return {'found': False, 'error': 'Browser not initialized'}

        try:
            page = await self.browser.new_page(
                user_agent=self.user_agents[2]
            )

            # Search DuckDuckGo for Wikipedia pages
            search_query = f'site:wikipedia.org "{company_name}"'
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(search_query)}"
            
            await page.goto(search_url, timeout=8000)
            await asyncio.sleep(2)

            # Look for Wikipedia results
            all_links = await page.query_selector_all('a')
            
            wikipedia_info = {'found': False}
            
            for link in all_links[:10]:
                try:
                    url = await link.get_attribute('href')
                    if url and 'wikipedia.org/wiki/' in url:
                        title = await link.inner_text()
                        # More flexible matching for Wikipedia titles
                        if title and (company_name.lower() in title.lower() or 
                                     any(word.lower() in title.lower() for word in company_name.split() if len(word) > 2)):
                            wikipedia_info = {
                                'found': True,
                                'url': url,
                                'title': title.strip()
                            }
                            break
                except:
                    continue

            await page.close()
            return wikipedia_info

        except Exception as e:
            logging.warning(f"Wikipedia search failed for {company_name}: {e}")
            return {'found': False, 'error': str(e)}

    def _is_likely_official_domain(self, url: str, company_name: str) -> bool:
        """Check if URL is likely the official company domain"""
        try:
            domain = self._extract_domain(url)
            company_clean = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            domain_clean = domain.replace('-', '').replace('.', '')
            
            # Skip social media and generic sites
            if any(site in domain for site in ['facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'wikipedia.org']):
                return False
            
            # Check if company name is in domain (exact match)
            if company_clean in domain_clean:
                return True
            
            # Check if domain contains significant part of company name
            if len(company_clean) >= 3 and company_clean in domain_clean:
                return True
                
            # Check for common patterns with company words
            company_words = [word.lower() for word in company_name.split() if len(word) > 2]
            for word in company_words:
                if word in domain and len(word) > 3:
                    # Additional validation - domain should be reasonably short and simple
                    if len(domain) < 30 and domain.count('.') <= 3:
                        return True
            
            # Check for acronyms (e.g., IBM -> ibm.com)
            if len(company_name.split()) > 1:
                acronym = ''.join([word[0].lower() for word in company_name.split() if word])
                if len(acronym) >= 2 and acronym in domain:
                    return True
                    
            return False
        except:
            return False

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ''

# Singleton instance for reuse
_web_validator = None

async def get_web_validator():
    """Get or create web validator instance"""
    global _web_validator
    if _web_validator is None:
        _web_validator = WebCompanyValidator()
        await _web_validator.__aenter__()
    return _web_validator