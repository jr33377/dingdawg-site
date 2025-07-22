#!/usr/bin/env python3
"""
Update ClickBank Affiliate Links with Actual Nickname
Updates all ClickBank links to use joe333777 as the affiliate
"""

import sqlite3
import re

def update_clickbank_links():
    """Update all ClickBank affiliate links with the actual nickname"""
    db_path = "amazon_intelligence.db"
    affiliate_nickname = "joe333777"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔗 Updating ClickBank affiliate links...")
    print(f"📝 Using affiliate nickname: {affiliate_nickname}")
    print("="*60)
    
    # Get all ClickBank products
    cursor.execute('''
        SELECT al.id, al.affiliate_link, p.asin, p.title
        FROM affiliate_links al
        JOIN product_opportunities p ON al.product_id = p.id
        WHERE al.network = 'ClickBank'
    ''')
    
    clickbank_links = cursor.fetchall()
    updated_count = 0
    
    for link_id, old_link, asin, title in clickbank_links:
        # Extract vendor from the old link
        vendor_match = re.search(r'vendor=(\w+)', old_link)
        if vendor_match:
            vendor = vendor_match.group(1)
        else:
            # Extract from ASIN (CB-VENDOR format)
            vendor = asin.replace('CB-', '').lower()
        
        # Create new affiliate link
        new_link = f"https://hop.clickbank.net/?affiliate={affiliate_nickname}&vendor={vendor}"
        
        # Update the database
        cursor.execute('''
            UPDATE affiliate_links 
            SET affiliate_link = ?
            WHERE id = ?
        ''', (new_link, link_id))
        
        updated_count += 1
        print(f"✅ {updated_count:2d}. {title[:45]}...")
        print(f"    Vendor: {vendor}")
        print(f"    Link: {new_link}")
        print("-" * 60)
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Updated {updated_count} ClickBank affiliate links!")
    print(f"🔗 All links now use affiliate: {affiliate_nickname}")
    
    return updated_count

if __name__ == "__main__":
    print("🚀 ClickBank Affiliate Link Updater")
    print("="*60)
    
    updated = update_clickbank_links()
    
    if updated > 0:
        print(f"\n✅ SUCCESS: All ClickBank links updated!")
        print(f"💰 Ready to earn commissions from 15 ClickBank products")
        print(f"🎯 Next: Deploy to dingdawg.com and start earning!")
    else:
        print("❌ No ClickBank links found to update")