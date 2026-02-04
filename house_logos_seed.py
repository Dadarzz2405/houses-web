#!/usr/bin/env python3
"""
🎨 Update House Logos with Cloudinary URLs
This script updates the database directly with Cloudinary logo URLs
"""

import os
import sys

# Cloudinary URLs mapping
CLOUDINARY_LOGOS = {
    "Al-Ghuraab": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108364/Al-Ghuraab_szxjhl.png",
    "An-Nahl": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108374/An-Nahl_pelgou.png",
    "An-Nun": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108369/An-Nun_erm5nb.png",
    "Al-Adiyat": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108368/Al-Adiyat_l5h9eh.png",
    "Al-Hudhud": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108363/Al-HudHud_oblb0w.png",
    "An-Naml": "https://res.cloudinary.com/dntujhjkw/image/upload/v1770108363/An-Naml_hqfrmx.png",
}

def update_with_sqlalchemy():
    """Update using Flask-SQLAlchemy ORM"""
    try:
        # Import Flask app and models
        from app import app
        from models import db, House
        
        with app.app_context():
            print("=" * 60)
            print("🎨 UPDATING HOUSE LOGOS WITH CLOUDINARY URLS")
            print("=" * 60)
            print()
            
            updated_count = 0
            for house_name, logo_url in CLOUDINARY_LOGOS.items():
                house = House.query.filter_by(name=house_name).first()
                
                if house:
                    old_url = house.logo_url
                    house.logo_url = logo_url
                    print(f"✅ {house_name}")
                    print(f"   Old: {old_url or 'None'}")
                    print(f"   New: {logo_url}")
                    print()
                    updated_count += 1
                else:
                    print(f"⚠️  {house_name} - House not found in database")
                    print()
            
            # Commit all changes
            db.session.commit()
            
            print("=" * 60)
            print(f"✅ Successfully updated {updated_count} houses")
            print("=" * 60)
            print()
            
            # Verify the updates
            print("🔍 VERIFICATION - Current Logo URLs:")
            print("=" * 60)
            all_houses = House.query.order_by(House.name).all()
            for house in all_houses:
                print(f"{house.name}: {house.logo_url}")
            print()
            
            return True
            
    except ImportError as e:
        print(f"❌ Error: Could not import app or models: {e}")
        print("   Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False

def update_with_raw_sql():
    """Update using raw SQL (fallback method)"""
    try:
        from app import app
        from models import db
        
        with app.app_context():
            print("=" * 60)
            print("🎨 UPDATING HOUSE LOGOS (RAW SQL METHOD)")
            print("=" * 60)
            print()
            
            for house_name, logo_url in CLOUDINARY_LOGOS.items():
                sql = "UPDATE houses SET logo_url = :url WHERE name = :name"
                result = db.session.execute(sql, {'url': logo_url, 'name': house_name})
                print(f"✅ {house_name}: Updated")
            
            db.session.commit()
            print()
            print("=" * 60)
            print("✅ All updates committed successfully")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generate_sql_file():
    """Generate a standalone SQL file for manual execution"""
    sql_content = "-- Update House Logos with Cloudinary URLs\n\n"
    
    for house_name, logo_url in CLOUDINARY_LOGOS.items():
        sql_content += f"UPDATE houses SET logo_url = '{logo_url}' WHERE name = '{house_name}';\n"
    
    sql_content += "\n-- Verify updates\n"
    sql_content += "SELECT name, logo_url FROM houses ORDER BY name;\n"
    
    with open('update_logos_manual.sql', 'w') as f:
        f.write(sql_content)
    
    print("✅ Generated update_logos_manual.sql")
    print("   You can run this manually if the Python methods don't work")
    return True

if __name__ == "__main__":
    print()
    print("🎨 CLOUDINARY LOGO UPDATER")
    print("=" * 60)
    print()
    
    # Try SQLAlchemy ORM method first
    print("📝 Method 1: Trying Flask-SQLAlchemy ORM...")
    print()
    if update_with_sqlalchemy():
        print("✅ SUCCESS! Database updated successfully")
        sys.exit(0)
    
    print()
    print("⚠️  ORM method failed, trying raw SQL...")
    print()
    
    # Try raw SQL method
    print("📝 Method 2: Trying Raw SQL...")
    print()
    if update_with_raw_sql():
        print("✅ SUCCESS! Database updated successfully")
        sys.exit(0)
    
    print()
    print("⚠️  Both methods failed. Generating SQL file for manual execution...")
    print()
    
    # Generate SQL file as last resort
    generate_sql_file()
    
    print()
    print("=" * 60)
    print("⚠️  MANUAL ACTION REQUIRED")
    print("=" * 60)
    print("Run the generated SQL file manually:")
    print("  • SQLite: sqlite3 app.db < update_logos_manual.sql")
    print("  • PostgreSQL: psql -d your_database < update_logos_manual.sql")
    print("=" * 60)
    print()
    
    sys.exit(1)