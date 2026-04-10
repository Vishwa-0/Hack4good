# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
import os

def scrape_instagram_profile(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    # Use system chromedriver installed via packages.txt
    # Streamlit Cloud puts chromedriver in PATH
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(4)
        
        # Check for login wall
        if "login" in driver.current_url:
            driver.quit()
            raise Exception("Instagram requires login. Use manual entry.")
        
        meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
        followers_match = re.search(r'([\d,]+)\s+Followers', meta_desc)
        following_match = re.search(r'([\d,]+)\s+Following', meta_desc)
        posts_match = re.search(r'([\d,]+)\s+Posts', meta_desc)
        
        followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
        following = int(following_match.group(1).replace(',', '')) if following_match else 0
        posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
        
        username = url.rstrip('/').split('/')[-1]
        username_length = len(username)
        nums_username = sum(c.isdigit() for c in username)
        nums_length_username = nums_username / username_length if username_length else 0.0
        
        try:
            fullname = driver.find_element(By.XPATH, "//h1 | //h2[contains(@class, 'x1lliihq')]").text.strip()
        except:
            fullname = username
        
        fullname_words = len(fullname.split())
        fullname_len = len(fullname)
        nums_fullname = sum(c.isdigit() for c in fullname)
        nums_length_fullname = nums_fullname / fullname_len if fullname_len else 0.0
        name_equals_username = 1 if fullname.lower() == username.lower() else 0
        
        try:
            bio = driver.find_element(By.XPATH, "//div[contains(@class, 'x7a106z')]//span").text
            description_length = len(bio)
        except:
            description_length = 0
        
        external_url = 1 if driver.find_elements(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'instagram'))]") else 0
        private = 1 if driver.find_elements(By.XPATH, "//h2[contains(text(), 'This Account is Private')]") else 0
        
        try:
            pic = driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            profile_pic = 0 if "44884218" in pic.get_attribute("src") else 1
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
