# scraper.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json

def scrape_instagram_profile(url):
    """
    Scrapes public Instagram profile data using undetected-chromedriver.
    Works on both local machines and Streamlit Cloud (with packages.txt having 'chromium').
    """
    
    # Configure Chrome options for stealth and headless operation
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")          # New headless mode (less detectable)
    options.add_argument("--no-sandbox")            # Required for cloud environments
    options.add_argument("--disable-dev-shm-usage") # Prevent memory issues
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options, version_main=120)  # Specify Chrome version to avoid mismatch
    
    try:
        driver.get(url)
        time.sleep(4)  # Allow page to fully load JavaScript
        
        # Check if we're being asked to login
        if "login" in driver.current_url or "accounts/login" in driver.current_url:
            driver.quit()
            raise Exception("Instagram requires login. Use manual entry.")
        
        # Method 1: Extract from meta description (most common)
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
            followers_match = re.search(r'([\d,]+)\s+Followers', meta_desc)
            following_match = re.search(r'([\d,]+)\s+Following', meta_desc)
            posts_match = re.search(r'([\d,]+)\s+Posts', meta_desc)
            
            followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
            following = int(following_match.group(1).replace(',', '')) if following_match else 0
            posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
        except:
            # Method 2: Try JSON-LD structured data in page source
            page_source = driver.page_source
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page_source, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    followers = data.get('mainEntityofPage', {}).get('interactionStatistic', [{}])[0].get('userInteractionCount', 0)
                    following = 0  # Not always available
                    posts = 0
                except:
                    followers = following = posts = 0
            else:
                followers = following = posts = 0
        
        # Extract username from URL
        username = url.rstrip('/').split('/')[-1]
        username_length = len(username)
        nums_in_username = sum(c.isdigit() for c in username)
        nums_length_username = nums_in_username / username_length if username_length > 0 else 0.0
        
        # Extract full name
        try:
            # Try multiple possible selectors for full name
            fullname_elem = driver.find_element(By.XPATH, "//h1 | //h2[contains(@class, 'x1lliihq')] | //span[@class='x1lliihq']")
            fullname = fullname_elem.text.strip()
        except:
            fullname = username
        
        fullname_words = len(fullname.split())
        fullname_length = len(fullname)
        nums_in_fullname = sum(c.isdigit() for c in fullname)
        nums_length_fullname = nums_in_fullname / fullname_length if fullname_length > 0 else 0.0
        name_equals_username = 1 if fullname.lower() == username.lower() else 0
        
        # Extract bio/description length
        try:
            bio_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'x7a106z')]//span | //div[@class='_aa_c']//span")
            description_length = len(bio_elem.text)
        except:
            description_length = 0
        
        # Check for external URL
        external_url = 1 if driver.find_elements(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'instagram'))]") else 0
        
        # Check if private
        private = 1 if driver.find_elements(By.XPATH, "//h2[contains(text(), 'This Account is Private')]") else 0
        
        # Profile picture check (custom vs default)
        try:
            pic_elem = driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            pic_src = pic_elem.get_attribute("src")
            # Default Instagram profile pic contains this pattern
            profile_pic = 0 if "44884218" in pic_src else 1
        except:
            profile_pic = 0
        
        driver.quit()
        
        return {
            'profile pic': profile_pic,
            'nums/length username': round(nums_length_username, 4),
            'fullname words': fullname_words,
            'nums/length fullname': round(nums_length_fullname, 4),
            'name==username': name_equals_username,
            'description length': description_length,
            'external URL': external_url,
            'private': private,
            '#posts': posts,
            '#followers': followers,
            '#follows': following
        }
    
    except Exception as e:
        driver.quit()
        raise Exception(f"Scraping failed: {str(e)}")
