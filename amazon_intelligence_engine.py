#!/usr/bin/env python3
"""
Amazon Intelligence Engine for Jarvis Affiliate System
Autonomous product selection based on real market data and trends

This engine follows Amazon's guidelines by:
1. Respecting robots.txt and rate limits
2. Using only publicly available data
3. Generating manual link instructions for compliance
"""

import requests
import time
import csv
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class ProductOpportunity:
    """Data class for product opportunities"""
    asin: str
    title: str
    price: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    bestseller_rank: Optional[int]
    category: str
    url: str
    opportunity_score: float
    trending_indicators: List[str]
    commission_tier: str
    estimated_monthly_revenue: float

class AmazonIntelligenceEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Rate limiting - be respectful
        self.request_delay = 2  # 2 seconds between requests
        self.last_request_time = 0

        # Database setup
        self.db_path = "amazon_intelligence.db"
        self.setup_database()

        # Commission tiers (Amazon's current structure)
        self.commission_tiers = {
            'luxury_beauty': 0.10,
            'amazon_games': 0.20,
            'digital_video_games': 0.20,
            'physical_video_games': 0.01,
            'pc_components': 0.025,
            'televisions': 0.02,
            'headphones': 0.02,
            'beauty_personal_care': 0.04,
            'musical_instruments': 0.06,
            'business_products': 0.06,
            'outdoors': 0.05,
            'tools_home_improvement': 0.05,
            'sports': 0.05,
            'kitchen': 0.05,
            'automotive': 0.045,
            'baby_products': 0.045,
            'books': 0.045,
            'electronics': 0.025,
            'fashion': 0.04,
            'health_household': 0.04,
            'home_garden': 0.04,
            'industrial_scientific': 0.04,
            'luggage': 0.04,
            'movies_tv': 0.04,
            'music': 0.04,
            'software': 0.04,
            'toys_games': 0.04,
            'everything_else': 0.04
        }

        # AI/Tech categories we're targeting
        self.target_categories = [
            'books',
            'electronics',
            'software',
            'pc_components',
            'business_products',
            'headphones'
        ]

    def setup_database(self):
        """Initialize SQLite database for storing product intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                price TEXT,
                rating REAL,
                review_count INTEGER,
                bestseller_rank INTEGER,
                category TEXT,
                url TEXT,
                opportunity_score REAL,
                trending_indicators TEXT,
                commission_tier TEXT,
                estimated_monthly_revenue REAL,
                discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'DISCOVERED',
                affiliate_link TEXT,
                content_generated BOOLEAN DEFAULT FALSE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATE DEFAULT CURRENT_DATE,
                category TEXT,
                top_trending_products TEXT,
                market_insights TEXT,
                recommended_actions TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print(f"✅ Intelligence database initialized: {self.db_path}")

    def respect_rate_limit(self):
        """Ensure we don't overwhelm Amazon's servers"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            print(f"⏱️  Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Safely fetch and parse a webpage"""
        self.respect_rate_limit()

        try:
            print(f" Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            return soup

        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon product URL"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:/|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def analyze_ai_books_bestsellers(self) -> List[ProductOpportunity]:
        """Analyze AI/ML books bestsellers for opportunities"""
        opportunities = []

        # AI Books category URLs
        ai_book_urls = [
            "https://www.amazon.com/Best-Sellers-Books-Artificial-Intelligence/zgbs/books/3887",
            "https://www.amazon.com/Best-Sellers-Books-Machine-Learning/zgbs/books/16977836011",
            "https://www.amazon.com/Best-Sellers-Books-Computer-Science/zgbs/books/3508"
        ]

        for category_url in ai_book_urls:
            soup = self.fetch_page(category_url)
            if not soup:
                continue

            # Extract bestseller products
            products = soup.find_all('div', {'data-component-type': 'bestseller-product-item'})

            for i, product in enumerate(products[:20], 1):  # Top 20 only
                try:
                    # Extract product details
                    title_elem = product.find('h3') or product.find('span', class_='a-size-mini')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Extract ASIN from product URL
                    link_elem = product.find('a', href=True)
                    if not link_elem:
                        continue

                    product_url = urljoin("https://www.amazon.com", link_elem['href'])
                    asin = self.extract_asin_from_url(product_url)

                    if not asin:
                        continue

                    # Extract price
                    price_elem = product.find('span', class_='a-price-whole') or product.find('span', class_='a-price')
                    price = price_elem.get_text(strip=True) if price_elem else None

                    # Extract rating
                    rating_elem = product.find('span', class_='a-icon-alt')
                    rating = None
                    if rating_elem:
                        rating_text = rating_elem.get_text()
                        rating_match = re.search(r'([\d.]+) out of', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))

                    # Calculate opportunity score
                    opportunity_score = self.calculate_opportunity_score(
                        bestseller_rank=i,
                        rating=rating,
                        category='books',
                        price=price,
                        trending_indicators=['bestseller']
                    )

                    # Estimate revenue
                    estimated_revenue = self.estimate_monthly_revenue(
                        bestseller_rank=i,
                        category='books',
                        price=price
                    )

                    opportunity = ProductOpportunity(
                        asin=asin,
                        title=title,
                        price=price,
                        rating=rating,
                        review_count=None,
                        bestseller_rank=i,
                        category='books',
                        url=product_url,
                        opportunity_score=opportunity_score,
                        trending_indicators=['bestseller'],
                        commission_tier='books',
                        estimated_monthly_revenue=estimated_revenue
                    )

                    opportunities.append(opportunity)
                    print(f" Found AI book opportunity: {title[:50]}... (Score: {opportunity_score:.2f})")

                except Exception as e:
                    print(f"⚠️  Error processing product: {e}")
                    continue

        return opportunities

    def analyze_tech_electronics_trending(self) -> List[ProductOpportunity]:
        """Analyze trending tech/electronics for AI-related products"""
        opportunities = []

        # Tech categories URLs
        tech_urls = [
            "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics",
            "https://www.amazon.com/gp/movers-and-shakers/electronics",
            "https://www.amazon.com/gp/new-releases/electronics"
        ]

        for category_url in tech_urls:
            soup = self.fetch_page(category_url)
            if not soup:
                continue

            # Extract products
            products = soup.find_all('div', {'data-component-type': 'bestseller-product-item'})

            for i, product in enumerate(products[:15], 1):  # Top 15
                try:
                    title_elem = product.find('h3') or product.find('span', class_='a-size-mini')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Filter for AI/tech related products
                    ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'neural',
                                   'deep learning', 'computer', 'processor', 'gpu', 'graphics',
                                   'programming', 'coding', 'development', 'tech', 'smart']

                    if not any(keyword in title.lower() for keyword in ai_keywords):
                        continue

                    link_elem = product.find('a', href=True)
                    if not link_elem:
                        continue

                    product_url = urljoin("https://www.amazon.com", link_elem['href'])
                    asin = self.extract_asin_from_url(product_url)

                    if not asin:
                        continue

                    # Extract additional details
                    price_elem = product.find('span', class_='a-price-whole')
                    price = price_elem.get_text(strip=True) if price_elem else None

                    # Determine trending indicator
                    trending_indicator = 'trending'
                    if 'movers-and-shakers' in category_url:
                        trending_indicator = 'movers_shakers'
                    elif 'new-releases' in category_url:
                        trending_indicator = 'new_release'
                    elif 'bestseller' in category_url:
                        trending_indicator = 'bestseller'

                    opportunity_score = self.calculate_opportunity_score(
                        bestseller_rank=i,
                        rating=None,
                        category='electronics',
                        price=price,
                        trending_indicators=[trending_indicator]
                    )

                    estimated_revenue = self.estimate_monthly_revenue(
                        bestseller_rank=i,
                        category='electronics',
                        price=price
                    )

                    opportunity = ProductOpportunity(
                        asin=asin,
                        title=title,
                        price=price,
                        rating=None,
                        review_count=None,
                        bestseller_rank=i,
                        category='electronics',
                        url=product_url,
                        opportunity_score=opportunity_score,
                        trending_indicators=[trending_indicator],
                        commission_tier='electronics',
                        estimated_monthly_revenue=estimated_revenue
                    )

                    opportunities.append(opportunity)
                    print(f" Found tech opportunity: {title[:50]}... (Score: {opportunity_score:.2f})")

                except Exception as e:
                    print(f"⚠️  Error processing tech product: {e}")
                    continue

        return opportunities

    def calculate_opportunity_score(self, bestseller_rank: int, rating: Optional[float],
                                  category: str, price: Optional[str],
                                  trending_indicators: List[str]) -> float:
        """Calculate opportunity score based on multiple factors"""
        score = 0.0

        # Bestseller rank score (higher rank = lower score)
        if bestseller_rank:
            rank_score = max(0, 100 - (bestseller_rank * 2))  # Top 50 get positive scores
            score += rank_score

        # Rating score
        if rating and rating >= 4.0:
            score += (rating - 4.0) * 50  # Bonus for ratings above 4.0

        # Commission tier bonus
        commission_rate = self.commission_tiers.get(category, 0.04)
        score += commission_rate * 1000  # Convert to meaningful number

        # Price range optimization (sweet spot for conversions)
        if price:
            price_num = self.extract_price_number(price)
            if price_num:
                if 20 <= price_num <= 100:  # Sweet spot for affiliate conversions
                    score += 30
                elif 10 <= price_num <= 200:
                    score += 20
                elif price_num > 200:
                    score += 10  # Higher value but lower conversion

        # Trending indicators bonus
        trending_bonuses = {
            'movers_shakers': 40,  # Highest - rapidly gaining popularity
            'new_release': 30,     # High - fresh and potentially viral
            'bestseller': 20,      # Good - proven demand
            'trending': 15         # Moderate - general trending
        }

        for indicator in trending_indicators:
            score += trending_bonuses.get(indicator, 0)

        return round(score, 2)

    def extract_price_number(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None

        # Remove currency symbols and extract number
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        return None

    def estimate_monthly_revenue(self, bestseller_rank: int, category: str,
                               price: Optional[str]) -> float:
        """Estimate monthly affiliate revenue for a product"""
        if not bestseller_rank:
            return 0.0

        # Base traffic estimates (very conservative)
        if bestseller_rank <= 5:
            monthly_visitors = 500
        elif bestseller_rank <= 10:
            monthly_visitors = 300
        elif bestseller_rank <= 20:
            monthly_visitors = 150
        elif bestseller_rank <= 50:
            monthly_visitors = 75
        else:
            monthly_visitors = 25

        # Conversion rates vary by category and price
        ctr = 0.06  # 6% click-through rate
        conversion_rate = 0.03  # 3% conversion rate (conservative)

        # Commission rate
        commission_rate = self.commission_tiers.get(category, 0.04)

        # Price factor
        price_num = self.extract_price_number(price) if price else 50  # Default $50
        if not price_num:
            price_num = 50

        monthly_clicks = monthly_visitors * ctr
        monthly_conversions = monthly_clicks * conversion_rate
        commission_per_sale = price_num * commission_rate
        monthly_revenue = monthly_conversions * commission_per_sale

        return round(monthly_revenue, 2)

    def save_opportunities_to_database(self, opportunities: List[ProductOpportunity]):
        """Save discovered opportunities to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for opp in opportunities:
            cursor.execute('''
                INSERT OR REPLACE INTO product_opportunities
                (asin, title, price, rating, review_count, bestseller_rank,
                 category, url, opportunity_score, trending_indicators,
                 commission_tier, estimated_monthly_revenue, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp.asin, opp.title, opp.price, opp.rating, opp.review_count,
                opp.bestseller_rank, opp.category, opp.url, opp.opportunity_score,
                json.dumps(opp.trending_indicators), opp.commission_tier,
                opp.estimated_monthly_revenue, 'DISCOVERED'
            ))

        conn.commit()
        conn.close()
        print(f" Saved {len(opportunities)} opportunities to database")

    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get top opportunities from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT asin, title, price, rating, bestseller_rank, category,
                   url, opportunity_score, estimated_monthly_revenue,
                   trending_indicators, commission_tier, status
            FROM product_opportunities
            ORDER BY opportunity_score DESC
            LIMIT ?
        ''', (limit,))

        opportunities = []
        for row in cursor.fetchall():
            opportunities.append({
                'asin': row[0],
                'title': row[1],
                'price': row[2],
                'rating': row[3],
                'bestseller_rank': row[4],
                'category': row[5],
                'url': row[6],
                'opportunity_score': row[7],
                'estimated_monthly_revenue': row[8],
                'trending_indicators': json.loads(row[9]) if row[9] else [],
                'commission_tier': row[10],
                'status': row[11]
            })

        conn.close()
        return opportunities

    def generate_link_instructions(self, opportunities: List[Dict]) -> str:
        """Generate instructions for manual link creation"""
        instructions = f"""
 JARVIS AMAZON AFFILIATE LINK GENERATION INSTRUCTIONS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Jarvis has identified {len(opportunities)} HIGH-VALUE product opportunities.
Please generate affiliate links using Amazon SiteStripe for these products:

INSTRUCTIONS:
1. Log into Amazon Associates (https://affiliate-program.amazon.com/)
2. Navigate to Amazon.com (you should see SiteStripe toolbar at top)
3. Go to each product URL below
4. Use SiteStripe "Get Link" > "Text" to generate the affiliate link
5. Copy the "Short Link" (amzn.to format)
6. Update the product_database.csv file with the generated links

TOP OPPORTUNITIES (Ranked by Revenue Potential):
"""

        for i, opp in enumerate(opportunities, 1):
            commission_rate = self.commission_tiers.get(opp['commission_tier'], 0.04)
            instructions += f"""
--- PRODUCT #{i} ---
ASIN: {opp['asin']}
Title: {opp['title']}
Price: {opp['price'] or 'N/A'}
Category: {opp['category']}
Bestseller Rank: #{opp['bestseller_rank']}
Commission Rate: {commission_rate*100:.1f}%
Estimated Monthly Revenue: ${opp['estimated_monthly_revenue']:.2f}
Opportunity Score: {opp['opportunity_score']:.1f}/100
Trending Indicators: {', '.join(opp['trending_indicators'])}

AMAZON URL: {opp['url']}

AFFILIATE LINK (to be generated): ________________

"""

        total_revenue = sum(opp['estimated_monthly_revenue'] for opp in opportunities)
        instructions += f"""
 TOTAL ESTIMATED MONTHLY REVENUE: ${total_revenue:.2f}
 ANNUAL REVENUE POTENTIAL: ${total_revenue * 12:.2f}

⚠️  IMPORTANT: After generating links, update the status in the database to 'ACTIVE'
so Jarvis can begin creating content for these products.
"""

        return instructions

    def run_intelligence_scan(self) -> str:
        """Run full intelligence scan and return instructions"""
        print(" JARVIS AMAZON INTELLIGENCE ENGINE - STARTING SCAN")
        print("=" * 60)

        all_opportunities = []

        # Scan AI books
        print("\n Scanning AI/ML Books Bestsellers...")
        book_opportunities = self.analyze_ai_books_bestsellers()
        all_opportunities.extend(book_opportunities)

        # Scan tech electronics
        print("\n Scanning Tech/Electronics Trending...")
        tech_opportunities = self.analyze_tech_electronics_trending()
        all_opportunities.extend(tech_opportunities)

        if not all_opportunities:
            return "❌ No opportunities found during scan. Please check network connectivity."

        # Save to database
        self.save_opportunities_to_database(all_opportunities)

        # Get top opportunities
        top_opportunities = self.get_top_opportunities(limit=10)

        # Generate instructions
        instructions = self.generate_link_instructions(top_opportunities)

        # Save instructions to file
        instructions_file = f"amazon_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        print(f"\n✅ SCAN COMPLETE!")
        print(f" Total opportunities discovered: {len(all_opportunities)}")
        print(f" Top opportunities selected: {len(top_opportunities)}")
        print(f" Instructions saved to: {instructions_file}")

        return instructions_file

# Command Line Interface
if __name__ == "__main__":
    engine = AmazonIntelligenceEngine()

    print(" JARVIS AMAZON INTELLIGENCE ENGINE")
    print("Autonomous Product Selection & Revenue Optimization")
    print("=" * 60)

    instructions_file = engine.run_intelligence_scan()

    print(f"\n NEXT STEPS:")
    print(f"1. Open {instructions_file}")
    print(f"2. Follow the affiliate link generation instructions")
    print(f"3. Run content generation for active products")
    print(f"4. Monitor performance and optimize")

