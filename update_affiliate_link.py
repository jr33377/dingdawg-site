#!/usr/bin/env python3
"""
Affiliate Link Updater for Jarvis Affiliate System
Updates the product database with a manually generated affiliate link and sets the product status to 'ACTIVE'.
"""

import sqlite3
import sys
from datetime import datetime

def update_product_link(asin: str, affiliate_link: str):
    """
    Updates a specific product in the database with its affiliate link.
    """
    db_path = "amazon_intelligence.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the product exists
    cursor.execute("SELECT id FROM product_opportunities WHERE asin = ?", (asin,))
    product = cursor.fetchone()

    if not product:
        print(f"❌ Error: No product found with ASIN '{asin}'. Please check the ASIN.")
        conn.close()
        return

    # Update the product record
    try:
        cursor.execute("""
            UPDATE product_opportunities
            SET affiliate_link = ?, status = 'ACTIVE'
            WHERE asin = ?
        """, (affiliate_link, asin))
        conn.commit()
        print(f"✅ Successfully updated ASIN {asin} with new affiliate link.")
        print(f"   Product is now 'ACTIVE' and ready for content generation.")
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- Jarvis Affiliate Link Updater ---")
    if len(sys.argv) != 3:
        print("\nUsage: python update_affiliate_link.py <PRODUCT_ASIN> \"<AFFILIATE_LINK>\"")
        print("Example: python update_affiliate_link.py B08B3FZRBC \"amzn.to/123xyz\"")
        sys.exit(1)

    product_asin = sys.argv[1]
    product_link = sys.argv[2]

    update_product_link(product_asin, product_link)
