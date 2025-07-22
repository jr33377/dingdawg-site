#!/usr/bin/env python3
"""
Batch Review Generator for Amazon Compliance
Generates structured product reviews for all active products
"""

import os
import sys
import sqlite3
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ReviewBatchGenerator:
    def __init__(self):
        self.db_path = "amazon_intelligence.db"
        self.content_path = "content/posts"
        
        # Initialize OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        self.client = OpenAI(api_key=api_key)
        
        # Ensure content directory exists
        os.makedirs(self.content_path, exist_ok=True)
    
    def get_active_products(self):
        """Get all products with Amazon affiliate links"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.asin, p.title, p.price, p.category, p.opportunity_score,
                   al.affiliate_link
            FROM product_opportunities p
            JOIN affiliate_links al ON p.id = al.product_id
            WHERE al.network = 'Amazon' AND p.status = 'PARTIAL_ACTIVE'
            ORDER BY p.opportunity_score DESC
        ''')
        
        products = cursor.fetchall()
        conn.close()
        return products
    
    def generate_structured_review(self, title, price, category, affiliate_link):
        """Generate a structured product review"""
        
        prompt = f"""Write a comprehensive product review for "{title}" with the following structure:

## Overview
A 200-300 word overview explaining what this product is, who makes it, and why it's significant in the {category} category.

## Key Features
List 4-5 key features or capabilities of this product.

## Pros and Cons
**Pros:**
- List 3-4 major advantages

**Cons:** 
- List 2-3 potential drawbacks or limitations

## Who Should Buy This
Describe the ideal customer for this product in 2-3 sentences.

## Bottom Line
A 2-3 sentence summary recommendation.

Write in a professional, informative tone. Focus on practical benefits and real-world usage. Price reference: {price}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert product reviewer writing detailed, honest reviews for an affiliate marketing site. Write comprehensive, structured reviews that help readers make informed decisions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating review for {title}: {e}")
            return None
    
    def create_hugo_post(self, title, content, asin, affiliate_link, price, category):
        """Create Hugo markdown file with proper front matter"""
        
        # Create URL-friendly filename
        filename = title.lower()
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-'))
        filename = '-'.join(filename.split())
        filename = f"{filename}-review"
        
        current_date = datetime.now().isoformat()
        
        # Hugo front matter with SEO optimization
        front_matter = f"""---
title: "{title} Review - Complete Analysis & Buying Guide"
date: {current_date}
draft: false
tags: ["{category}", "review", "affiliate", "buying-guide"]
categories: ["{category}"]
description: "Detailed review of {title}. Features, pros, cons, and buying recommendations."
schema: "Product"
asin: "{asin}"
price: "{price}"
---

{content}

---

## Get This Product

Ready to purchase? **[Buy {title} on Amazon →]({affiliate_link})**

*As an Amazon Associate, we earn from qualifying purchases. This helps support our site and allows us to continue providing detailed product reviews.*

---

*Last updated: {datetime.now().strftime('%B %d, %Y')}*"""
        
        filepath = os.path.join(self.content_path, f"{filename}.md")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
        
        print(f"✅ Created: {filepath}")
        return filepath
    
    def generate_all_reviews(self):
        """Generate reviews for all active products"""
        products = self.get_active_products()
        
        if not products:
            print("❌ No active products found with Amazon affiliate links")
            return
        
        print(f"🚀 Generating reviews for {len(products)} products...")
        print("="*60)
        
        generated_files = []
        
        for asin, title, price, category, score, affiliate_link in products:
            print(f"\n📝 Generating review for: {title[:50]}...")
            
            # Generate structured review content
            content = self.generate_structured_review(title, price, category, affiliate_link)
            
            if content:
                # Create Hugo post
                filepath = self.create_hugo_post(title, content, asin, affiliate_link, price, category)
                generated_files.append(filepath)
                print(f"   ✅ Review completed")
            else:
                print(f"   ❌ Failed to generate review")
        
        print(f"\n🎉 Batch generation complete!")
        print(f"📊 Generated {len(generated_files)} product reviews")
        print(f"📁 Files created in: {self.content_path}/")
        
        return generated_files
    
    def build_hugo_site(self):
        """Build the Hugo site"""
        print("\n🔨 Building Hugo site...")
        
        # Check if hugo is available
        import subprocess
        try:
            result = subprocess.run(['hugo', 'version'], capture_output=True, text=True)
            print(f"Hugo version: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Hugo not found. Using local hugo binary...")
        
        # Build site
        try:
            result = subprocess.run(['./hugo'], cwd='.', capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Hugo site built successfully!")
                print("📁 Static files ready in: public/")
                return True
            else:
                print(f"❌ Hugo build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error building site: {e}")
            return False

if __name__ == "__main__":
    print("🚀 URGENT: Amazon Compliance - Batch Review Generator")
    print("="*60)
    
    generator = ReviewBatchGenerator()
    
    # Generate all reviews
    generated_files = generator.generate_all_reviews()
    
    if generated_files:
        # Build Hugo site
        generator.build_hugo_site()
        
        print("\n🌐 NEXT STEPS FOR DEPLOYMENT:")
        print("1. Upload public/ folder to dingdawg.com hosting")
        print("2. Configure DNS to point to hosting provider") 
        print("3. Enable SSL/HTTPS")
        print("4. Submit to Amazon for review")
        
    else:
        print("❌ No reviews generated - cannot proceed with deployment")