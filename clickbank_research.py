#!/usr/bin/env python3
"""
ClickBank Product Research for AI & Tech Products
Finds high-gravity, high-commission digital products to complement Amazon physical products
"""

import requests
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class ClickBankResearcher:
    def __init__(self):
        self.api_key = os.getenv("CLICKBANK_API_KEY")
        self.base_url = "https://api.clickbank.com/rest/1.3"
        self.db_path = "amazon_intelligence.db"
        
        if not self.api_key:
            raise ValueError("CLICKBANK_API_KEY not found in .env file")
    
    def search_products(self, category="computers-internet", min_gravity=20, max_results=15):
        """Search for high-converting ClickBank products"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # ClickBank API endpoint for product search
        endpoint = f"{self.base_url}/products"
        
        params = {
            "category": category,
            "gravity": f">{min_gravity}",
            "sort": "gravity",
            "limit": max_results
        }
        
        print(f"🔍 Searching ClickBank for {category} products with gravity > {min_gravity}...")
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                print(f"✅ Found {len(products)} products")
                return products
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return []
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []
    
    def get_ai_tech_categories(self):
        """Get relevant categories for AI and tech products"""
        return [
            "computers-internet",
            "business-investing", 
            "e-business-e-marketing",
            "employment-jobs",
            "software-services"
        ]
    
    def add_clickbank_products_to_db(self, products):
        """Add ClickBank products to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added_count = 0
        
        for product in products:
            try:
                # Extract product info
                product_id = product.get("site", "")
                title = product.get("title", "")
                description = product.get("description", "")
                gravity = product.get("gravity", 0)
                commission = product.get("commission", 0)
                price = product.get("price", 0)
                category = product.get("category", "")
                
                # Create ClickBank-specific ASIN (CB prefix)
                cb_asin = f"CB-{product_id}"
                
                # Insert into product_opportunities
                cursor.execute('''
                    INSERT OR REPLACE INTO product_opportunities 
                    (asin, title, price, category, opportunity_score, status,
                     estimated_monthly_revenue, clickbank_category, discovery_date)
                    VALUES (?, ?, ?, ?, ?, 'PENDING_LINKS', ?, ?, ?)
                ''', (
                    cb_asin, title, price, category, gravity,
                    commission * 10,  # Estimate monthly revenue
                    category, datetime.now()
                ))
                
                product_id_db = cursor.lastrowid
                
                # Create affiliate link placeholder
                cursor.execute('''
                    INSERT OR REPLACE INTO affiliate_links
                    (product_id, network, affiliate_link, commission_rate)
                    VALUES (?, 'ClickBank', ?, ?)
                ''', (
                    product_id_db, 
                    f"https://hop.clickbank.net/?affiliate=YOUR_ID&vendor={product_id}",
                    commission
                ))
                
                added_count += 1
                print(f"✅ Added: {title[:50]}... (Gravity: {gravity}, Commission: {commission}%)")
                
            except Exception as e:
                print(f"❌ Error adding product {product.get('title', 'Unknown')}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Added {added_count} ClickBank products to database!")
        return added_count
    
    def research_ai_products(self):
        """Research AI and tech products across multiple categories"""
        all_products = []
        categories = self.get_ai_tech_categories()
        
        for category in categories:
            print(f"\n📂 Researching category: {category}")
            products = self.search_products(category=category, max_results=5)
            all_products.extend(products)
        
        # Remove duplicates and sort by gravity
        unique_products = []
        seen_sites = set()
        
        for product in all_products:
            site = product.get("site", "")
            if site not in seen_sites:
                unique_products.append(product)
                seen_sites.add(site)
        
        # Sort by gravity (popularity)
        unique_products.sort(key=lambda x: x.get("gravity", 0), reverse=True)
        
        # Take top 15
        top_products = unique_products[:15]
        
        print(f"\n📊 Research Summary:")
        print(f"Total products found: {len(all_products)}")
        print(f"Unique products: {len(unique_products)}")
        print(f"Top products selected: {len(top_products)}")
        
        return top_products
    
    def show_research_results(self, products):
        """Display research results"""
        print(f"\n🎯 TOP 15 CLICKBANK AI/TECH PRODUCTS:")
        print("="*80)
        
        for i, product in enumerate(products[:15], 1):
            title = product.get("title", "")
            gravity = product.get("gravity", 0)
            commission = product.get("commission", 0)
            price = product.get("price", 0)
            category = product.get("category", "")
            
            print(f"{i:2d}. {title[:60]}...")
            print(f"    Gravity: {gravity} | Commission: {commission}% | Price: ${price}")
            print(f"    Category: {category}")
            print("-" * 80)

if __name__ == "__main__":
    print("🚀 ClickBank AI/Tech Product Research")
    print("="*60)
    
    try:
        researcher = ClickBankResearcher()
        
        # Research products
        products = researcher.research_ai_products()
        
        if products:
            # Show results
            researcher.show_research_results(products)
            
            # Add to database
            researcher.add_clickbank_products_to_db(products)
            
            print(f"\n✅ ClickBank integration complete!")
            print(f"📊 Database now contains Amazon + ClickBank products")
            print(f"🎯 Ready for 30-product content generation!")
        else:
            print("❌ No products found. Check API key and connection.")
            
    except Exception as e:
        print(f"❌ Error: {e}")