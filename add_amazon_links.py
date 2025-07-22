#!/usr/bin/env python3
"""
Add Amazon Affiliate Links to Multi-Network Database
Processes the provided Amazon affiliate links and adds them to the database
"""

import sqlite3
import sys
from datetime import datetime

class AmazonLinkProcessor:
    def __init__(self):
        self.db_path = "amazon_intelligence.db"
    
    def add_amazon_links(self):
        """Add the provided Amazon affiliate links"""
        
        # Your provided Amazon affiliate links
        amazon_links = [
            "https://amzn.to/4fb9WlC",
            "https://amzn.to/3IWejoh", 
            "https://amzn.to/45ga3J2",
            "https://amzn.to/3TPOgSf",
            "https://amzn.to/3GCUzpj",
            "https://amzn.to/46iajIB",
            "https://amzn.to/4lL0dVu",
            "https://www.amazon.com/dp/B0947BJ67M/ref=cm_sw_r_as_gl_api_gl_i_QQBJ8J600VHA2G0ASMNJ?linkCode=ml1&tag=33377701-20&linkId=14e117489c13e27fc71814cbfa64dc28",
            "https://amzn.to/44YkXSB",
            "https://amzn.to/4o5YX0U",
            "https://amzn.to/4flNpTj",
            "https://amzn.to/4m5tMRj",
            "https://amzn.to/46h1C1c",
            "https://amzn.to/418yCVQ"
        ]
        
        # Map to existing ASINs from our original 10 products
        existing_asins = [
            "B08B3FZRBC",  # Hands-On Machine Learning
            "B08N5WRWNW",  # Echo Dot 4th Gen  
            "B073LWHWJZ",  # Python Crash Course
            "B08LVBYZTC",  # Sony WH-1000XM4
            "B08ZJ6T86M",  # Logitech MX Master 3
            "B089DNQN2B",  # Pattern Recognition ML
            "B08F5N2DKS",  # Raspberry Pi 4
            "B07STGG1N2",  # Arduino Uno R3
            "B07YRWVY4N",  # NVIDIA RTX 3080
            "B08PNMQYSY"   # Microsoft Surface Studio
        ]
        
        # Map additional ASINs for your extra links
        additional_asins = [
            "B0947BJ67M",  # From your full Amazon URL
            "PLACEHOLDER_2",
            "PLACEHOLDER_3", 
            "PLACEHOLDER_4"
        ]
        
        all_asins = existing_asins + additional_asins
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("🔗 Processing Amazon affiliate links...")
        
        for i, link in enumerate(amazon_links):
            if i < len(all_asins):
                asin = all_asins[i]
                
                # Get product info
                cursor.execute("SELECT id, title FROM product_opportunities WHERE asin = ?", (asin,))
                product = cursor.fetchone()
                
                if product:
                    product_id, title = product
                    
                    # Add affiliate link
                    cursor.execute('''
                        INSERT OR REPLACE INTO affiliate_links 
                        (product_id, network, affiliate_link, commission_rate)
                        VALUES (?, 'Amazon', ?, 4.0)
                    ''', (product_id, link))
                    
                    # Update product status
                    cursor.execute('''
                        UPDATE product_opportunities 
                        SET status = 'PARTIAL_ACTIVE', last_content_update = ?
                        WHERE id = ?
                    ''', (datetime.now(), product_id))
                    
                    print(f"✅ Added Amazon link for: {title[:50]}...")
                    print(f"   ASIN: {asin}")
                    print(f"   Link: {link}")
                
                else:
                    print(f"⚠️ ASIN {asin} not found in database - skipping")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Processed {len(amazon_links)} Amazon affiliate links!")
        
        # Show current status
        self.show_status()
    
    def show_status(self):
        """Show current database status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.asin, p.title, p.status, COUNT(al.network) as networks,
                   GROUP_CONCAT(al.network) as network_list
            FROM product_opportunities p
            LEFT JOIN affiliate_links al ON p.id = al.product_id
            GROUP BY p.id
            ORDER BY p.opportunity_score DESC
        ''')
        
        results = cursor.fetchall()
        
        print("\n📊 Current Database Status:")
        print("="*80)
        
        for asin, title, status, network_count, networks in results:
            networks_display = networks if networks else "None"
            print(f"🔸 {title[:45]}...")
            print(f"   ASIN: {asin} | Status: {status}")  
            print(f"   Networks ({network_count}): {networks_display}")
            print("-" * 80)
        
        conn.close()

if __name__ == "__main__":
    processor = AmazonLinkProcessor()
    processor.add_amazon_links()