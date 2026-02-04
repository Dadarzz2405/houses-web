-- ✅ SQL Script to Update House Logos with Cloudinary URLs
-- Run this directly on your database or use it in a Python script

-- Update Al-Ghuraab
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108364/Al-Ghuraab_szxjhl.png'
WHERE name = 'Al-Ghuraab';

-- Update An-Nahl
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108374/An-Nahl_pelgou.png'
WHERE name = 'An-Nahl';

-- Update An-Nun
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108369/An-Nun_erm5nb.png'
WHERE name = 'An-Nun';

-- Update Al-Adiyat
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108368/Al-Adiyat_l5h9eh.png'
WHERE name = 'Al-Adiyat';

-- Update Al-Hudhud
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108363/Al-HudHud_oblb0w.png'
WHERE name = 'Al-Hudhud';

-- Update An-Naml
UPDATE houses 
SET logo_url = 'https://res.cloudinary.com/dntujhjkw/image/upload/v1770108363/An-Naml_hqfrmx.png'
WHERE name = 'An-Naml';

-- Verify the updates
SELECT name, logo_url FROM houses ORDER BY name;