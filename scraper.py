# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
import os

def scrape_instagram_profile(url):
    """
    Scrapes public Instagram profile data.
    Works on both local machines and Streamlit Cloud.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Detect environment and set up driver accordingly
    # Streamlit Cloud uses system chromedriver from packages.txt
    # Local machine can use webdriver-manager or system Chrome
    
    try:
        # First try: Use system chromedriver (works on Streamlit Cloud)
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        # Fallback: Use webdriver-manager for local development
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            raise Exception("Could not initialize ChromeDriver. Please ensure Chrome is installed.")
    
    try:
        driver.get(url)
        time.sleep(3)
        
        meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
        
        followers_match = re.search(r'([\d,]+)\s+Followers', meta_desc)
        following_match = re.search(r'([\d,]+)\s+Following', meta_desc)
        posts_match = re.search(r'([\d,]+)\s+Posts', meta_desc)
        
        followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
        following = int(following_match.group(1).replace(',', '')) if following_match else 0
        posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
        
        username = url.rstrip('/').split('/')[-1]
        username_length = len(username)
        nums_in_username = sum(c.isdigit() for c in username)
        nums_length_username = nums_in_username / username_length if username_length > 0 else 0
        
        try:
            fullname_elem = driver.find_element(By.XPATH, "//h1[contains(@class, 'x1lliihq')] | //h2[contains(@class, 'x1lliihq')]")
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
            bio_text = bio_elem.text
            description_length = len(bio_text)
        except:
            description_length = 0
        
        try:
            driver.find_element(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'instagram.com'))]")
            external_url = 1
        except:
            external_url = 0
        
        try:
            driver.find_element(By.XPATH, "//h2[contains(text(), 'This Account is Private')]")
            private = 1
        except:
            private = 0
        
        try:
            pic_elem = driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            pic_src = pic_elem.get_attribute("src")
            if "44884218_345707102882519_2446069589734326272_n" in pic_src:
                profile_pic = 0
            else:
                profile_pic = 1
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
