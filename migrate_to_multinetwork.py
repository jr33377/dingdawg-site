#!/usr/bin/env python3
"""
Database Migration: Single to Multi-Network Architecture
Migrates existing AAF database to support multiple affiliate networks (Amazon + ClickBank)
"""

import sqlite3
import sys
from datetime import datetime

def migrate_database():
    """Migrate existing database to multi-network schema"""
    db_path = "amazon_intelligence.db"
    
    print("🔄 Starting database migration to multi-network architecture...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Create new affiliate_links table
        print("📊 Creating affiliate_links table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                network TEXT NOT NULL,  -- 'Amazon', 'ClickBank', etc.
                affiliate_link TEXT NOT NULL,
                commission_rate REAL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE',
                FOREIGN KEY(product_id) REFERENCES product_opportunities(id),
                UNIQUE(product_id, network)
            )
        ''')
        
        # 2. Migrate existing Amazon links from product_opportunities table
        print("🔗 Migrating existing Amazon affiliate links...")
        cursor.execute('''
            SELECT id, affiliate_link 
            FROM product_opportunities 
            WHERE affiliate_link IS NOT NULL AND affiliate_link != ''
        ''')
        
        existing_links = cursor.fetchall()
        
        for product_id, affiliate_link in existing_links:
            cursor.execute('''
                INSERT OR REPLACE INTO affiliate_links 
                (product_id, network, affiliate_link, commission_rate)
                VALUES (?, 'Amazon', ?, 4.0)
            ''', (product_id, affiliate_link))
            print(f"   ✅ Migrated Amazon link for product ID {product_id}")
        
        # 3. Add new columns to product_opportunities for enhanced tracking
        print("📈 Adding enhanced tracking columns...")
        try:
            cursor.execute('ALTER TABLE product_opportunities ADD COLUMN clickbank_category TEXT')
            cursor.execute('ALTER TABLE product_opportunities ADD COLUMN multi_network_revenue REAL DEFAULT 0')
            cursor.execute('ALTER TABLE product_opportunities ADD COLUMN last_content_update TIMESTAMP')
        except sqlite3.OperationalError:
            print("   ℹ️ Columns already exist, skipping...")
        
        # 4. Create network performance tracking table
        print("📊 Creating network performance tracking...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES product_opportunities(id)
            )
        ''')
        
        # 5. Update product status logic for multi-network
        print("🔄 Updating status logic for multi-network support...")
        cursor.execute('''
            UPDATE product_opportunities 
            SET status = CASE 
                WHEN affiliate_link IS NOT NULL AND affiliate_link != '' THEN 'PARTIAL_ACTIVE'
                ELSE 'PENDING_LINKS'
            END
        ''')
        
        conn.commit()
        
        # Report migration results
        cursor.execute('SELECT COUNT(*) FROM affiliate_links WHERE network = "Amazon"')
        amazon_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM product_opportunities')
        total_products = cursor.fetchone()[0]
        
        print("\n✅ Migration completed successfully!")
        print(f"📊 Migration Summary:")
        print(f"   • Total products: {total_products}")
        print(f"   • Amazon links migrated: {amazon_count}")
        print(f"   • Ready for ClickBank integration: {total_products}")
        print(f"   • New tables created: affiliate_links, network_performance")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    db_path = "amazon_intelligence.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔍 Verifying migration...")
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['product_opportunities', 'affiliate_links', 'network_performance']
    for table in required_tables:
        if table in tables:
            print(f"   ✅ Table '{table}' exists")
        else:
            print(f"   ❌ Table '{table}' missing")
            return False
    
    # Check data integrity
    cursor.execute('SELECT COUNT(*) FROM affiliate_links')
    links_count = cursor.fetchone()[0]
    print(f"   📊 Total affiliate links: {links_count}")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("🚀 AAF Multi-Network Migration Tool")
    print("="*50)
    
    success = migrate_database()
    if success:
        verify_migration()
        print("\n🎉 Database is now ready for multi-network affiliate management!")
        print("Next steps:")
        print("1. Run: python update_affiliate_link_multinetwork.py")  
        print("2. Add ClickBank links for products")
        print("3. Generate enhanced content with multiple affiliate options")
    else:
        print("❌ Migration failed. Please check the error messages above.")
        sys.exit(1)