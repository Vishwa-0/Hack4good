# scraper.py (Enhanced with multiple fallback selectors)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json

def scrape_instagram_profile(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(options=options)
    except:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(4)  # Wait longer for dynamic content
        
        # Check if we hit a login wall
        if "login" in driver.current_url or "accounts/login" in driver.current_url:
            driver.quit()
            raise Exception("Instagram requires login. Use manual entry.")
        
        # Method 1: Try meta description (original approach)
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
            if meta_desc:
                followers_match = re.search(r'([\d,]+)\s+Followers', meta_desc)
                following_match = re.search(r'([\d,]+)\s+Following', meta_desc)
                posts_match = re.search(r'([\d,]+)\s+Posts', meta_desc)
                followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
                following = int(following_match.group(1).replace(',', '')) if following_match else 0
                posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
        except:
            followers = following = posts = 0
        
        # Method 2: Try JSON data in page source (newer Instagram)
        if followers == 0:
            page_source = driver.page_source
            # Look for JSON-LD structured data
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page_source, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    followers = data.get('mainEntityofPage', {}).get('interactionStatistic', [{}])[0].get('userInteractionCount', 0)
                except:
                    pass
        
        # Method 3: Try specific span elements (common selectors)
        if followers == 0:
            try:
                # Look for elements with "followers" text
                elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'followers')]/span")
                if elements:
                    followers_text = elements[0].get_attribute("title") or elements[0].text
                    followers = int(re.sub(r'[^\d]', '', followers_text))
            except:
                pass
        
        # If still zero, we likely failed - raise error for manual fallback
        if followers == 0 and following == 0 and posts == 0:
            driver.quit()
            raise Exception("Could not extract profile data. Instagram may be blocking automated access.")
        
        # Rest of feature extraction (username, fullname, bio, etc.)
        username = url.rstrip('/').split('/')[-1]
        username_length = len(username)
        nums_in_username = sum(c.isdigit() for c in username)
        nums_length_username = nums_in_username / username_length if username_length > 0 else 0
        
        try:
            fullname_elem = driver.find_element(By.XPATH, "//h1 | //h2[contains(@class, 'x1lliihq')]")
            fullname = fullname_elem.text.strip()
        except:
            fullname = username
        
        fullname_words = len(fullname.split())
        fullname_length = len(fullname)
        nums_in_fullname = sum(c.isdigit() for c in fullname)
        nums_length_fullname = nums_in_fullname / fullname_length if fullname_length > 0 else 0
        name_equals_username = 1 if fullname.lower() == username.lower() else 0
        
        try:
            bio_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'x7a106z')]//span")
            description_length = len(bio_elem.text)
        except:
            description_length = 0
        
        external_url = 1 if driver.find_elements(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'instagram'))]") else 0
        private = 1 if driver.find_elements(By.XPATH, "//h2[contains(text(), 'This Account is Private')]") else 0
        
        try:
            pic_elem = driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            pic_src = pic_elem.get_attribute("src")
            profile_pic = 0 if "44884218" in pic_src else 1
        except:
            profile_pic = 0
        
        driver.quit()
        
        return {
            'profile pic': profile_pic,
            'nums/length username': nums_length_username,
            'fullname words': fullname_words,
            'nums/length fullname': nums_length_fullname,
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
