#!/usr/bin/env python3
"""
Multi-Network Affiliate Link Manager for Jarvis Affiliate System
Updates products with affiliate links from multiple networks (Amazon, ClickBank, etc.)
"""

import sqlite3
import sys
import argparse
from datetime import datetime

class MultiNetworkLinkManager:
    def __init__(self):
        self.db_path = "amazon_intelligence.db"
    
    def add_affiliate_link(self, asin: str, network: str, affiliate_link: str, commission_rate: float = None):
        """Add or update affiliate link for a specific network"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get product ID from ASIN
            cursor.execute("SELECT id, title FROM product_opportunities WHERE asin = ?", (asin,))
            product = cursor.fetchone()
            
            if not product:
                print(f"❌ Error: No product found with ASIN '{asin}'")
                return False
            
            product_id, title = product
            
            # Set default commission rates by network
            if commission_rate is None:
                commission_rates = {
                    'Amazon': 4.0,
                    'ClickBank': 50.0,  # ClickBank typically higher
                    'ShareASale': 8.0,
                    'CJ': 6.0
                }
                commission_rate = commission_rates.get(network, 5.0)
            
            # Insert or update affiliate link
            cursor.execute('''
                INSERT OR REPLACE INTO affiliate_links 
                (product_id, network, affiliate_link, commission_rate, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_id, network, affiliate_link, commission_rate, datetime.now()))
            
            # Update product status based on available networks
            cursor.execute('''
                SELECT COUNT(*) FROM affiliate_links WHERE product_id = ?
            ''', (product_id,))
            
            link_count = cursor.fetchone()[0]
            
            # Update product status
            if link_count >= 2:
                new_status = 'FULLY_ACTIVE'  # Multiple networks
            elif link_count == 1:
                new_status = 'PARTIAL_ACTIVE'  # Single network
            else:
                new_status = 'PENDING_LINKS'
            
            cursor.execute('''
                UPDATE product_opportunities 
                SET status = ?, last_content_update = ?
                WHERE id = ?
            ''', (new_status, datetime.now(), product_id))
            
            # Initialize performance tracking
            cursor.execute('''
                INSERT OR REPLACE INTO network_performance
                (product_id, network, clicks, conversions, revenue)
                VALUES (?, ?, 0, 0, 0.0)
            ''', (product_id, network))
            
            conn.commit()
            
            print(f"✅ Successfully added {network} link for '{title[:50]}...'")
            print(f"   ASIN: {asin}")
            print(f"   Network: {network}")
            print(f"   Commission: {commission_rate}%")
            print(f"   Status: {new_status}")
            print(f"   Total Networks: {link_count}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            conn.close()
    
    def show_product_links(self, asin: str):
        """Display all affiliate links for a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.title, p.price, p.opportunity_score, p.status,
                   al.network, al.affiliate_link, al.commission_rate
            FROM product_opportunities p
            LEFT JOIN affiliate_links al ON p.id = al.product_id
            WHERE p.asin = ?
        ''', (asin,))
        
        results = cursor.fetchall()
        
        if not results:
            print(f"❌ No product found with ASIN '{asin}'")
            return
        
        # Display product info
        title, price, score, status = results[0][:4]
        print(f"\n📊 Product: {title}")
        print(f"   ASIN: {asin}")
        print(f"   Price: {price}")
        print(f"   Opportunity Score: {score}/100")
        print(f"   Status: {status}")
        
        print(f"\n🔗 Affiliate Links:")
        has_links = False
        for row in results:
            network, link, commission = row[4], row[5], row[6]
            if network:
                has_links = True
                print(f"   • {network}: {link} ({commission}% commission)")
        
        if not has_links:
            print("   ❌ No affiliate links configured")
        
        conn.close()
    
    def list_products_by_status(self, status_filter=None):
        """List all products with their network status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT p.asin, p.title, p.price, p.opportunity_score, p.status,
                   COUNT(al.network) as network_count,
                   GROUP_CONCAT(al.network) as networks
            FROM product_opportunities p
            LEFT JOIN affiliate_links al ON p.id = al.product_id
        '''
        
        if status_filter:
            query += f" WHERE p.status = '{status_filter}'"
        
        query += " GROUP BY p.id ORDER BY p.opportunity_score DESC"
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n📋 Product Status Report" + (f" (Filter: {status_filter})" if status_filter else ""))
        print("="*80)
        
        for row in results:
            asin, title, price, score, status, network_count, networks = row
            networks_str = networks if networks else "None"
            
            print(f"🔸 {title[:50]}...")
            print(f"   ASIN: {asin} | Price: {price} | Score: {score}/100")
            print(f"   Status: {status} | Networks ({network_count}): {networks_str}")
            print("-" * 80)
        
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Multi-Network Affiliate Link Manager')
    parser.add_argument('action', choices=['add', 'show', 'list'], 
                       help='Action to perform')
    parser.add_argument('--asin', help='Product ASIN')
    parser.add_argument('--network', help='Affiliate network (Amazon, ClickBank, etc.)')
    parser.add_argument('--link', help='Affiliate link URL')
    parser.add_argument('--commission', type=float, help='Commission rate percentage')
    parser.add_argument('--status', help='Filter products by status')
    
    args = parser.parse_args()
    
    manager = MultiNetworkLinkManager()
    
    if args.action == 'add':
        if not all([args.asin, args.network, args.link]):
            print("❌ Error: --asin, --network, and --link are required for 'add' action")
            sys.exit(1)
        
        manager.add_affiliate_link(args.asin, args.network, args.link, args.commission)
    
    elif args.action == 'show':
        if not args.asin:
            print("❌ Error: --asin is required for 'show' action")
            sys.exit(1)
        
        manager.show_product_links(args.asin)
    
    elif args.action == 'list':
        manager.list_products_by_status(args.status)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🤖 Multi-Network Affiliate Link Manager")
        print("="*50)
        print("Usage examples:")
        print("  python update_affiliate_link_multinetwork.py add --asin B08B3FZRBC --network Amazon --link 'amzn.to/123abc'")
        print("  python update_affiliate_link_multinetwork.py add --asin B08B3FZRBC --network ClickBank --link 'clickbank.net/hop/xyz'")
        print("  python update_affiliate_link_multinetwork.py show --asin B08B3FZRBC")
        print("  python update_affiliate_link_multinetwork.py list")
        print("  python update_affiliate_link_multinetwork.py list --status PENDING_LINKS")
    else:
        main()