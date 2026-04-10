# scraper.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re
import os

def close_instagram_popups(driver):
    """
    Attempts to dismiss any sign-up or login pop-up modals on Instagram.
    Returns True if a pop-up was closed, False otherwise.
    """
    close_button_selectors = [
        ("css", "div[role='dialog'] svg[aria-label='Close']"),
        ("xpath", "//*[local-name()='svg' and @aria-label='Close']"),
        ("xpath", "//button[contains(text(), 'Not Now')]"),
        ("xpath", "//div[@role='button' and contains(., 'Not Now')]"),
        ("css", "div[role='button'] [aria-label='Close']"),
    ]

    for selector_type, selector in close_button_selectors:
        try:
            wait = WebDriverWait(driver, 5)
            if selector_type == "xpath":
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            return True
        except (NoSuchElementException, TimeoutException):
            continue
    
    return False


def scrape_instagram_profile(url):
    """
    Scrapes public Instagram profile data.
    Automatically dismisses sign-up pop-ups if present.
    Works on Arch Linux (local) and Streamlit Cloud (deployed).
    """
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Determine browser executable path based on environment
    # Arch Linux: /usr/bin/chromium
    # Streamlit Cloud: /usr/bin/chromium (via packages.txt)
    if os.path.exists("/usr/bin/chromium"):
        browser_path = "/usr/bin/chromium"
    elif os.path.exists("/usr/bin/chromium-browser"):
        browser_path = "/usr/bin/chromium-browser"
    else:
        browser_path = None  # Let undetected-chromedriver find it
    
    driver_kwargs = {
        "options": options,
        "version_main": 120
    }
    if browser_path:
        driver_kwargs["browser_executable_path"] = browser_path
    
    driver = uc.Chrome(**driver_kwargs)
    
    try:
        driver.get(url)
        time.sleep(4)
        
        # Check for login wall (full page redirect)
        if "login" in driver.current_url or "accounts/login" in driver.current_url:
            driver.quit()
            raise Exception("Instagram requires login. Use manual entry.")
        
        # Dismiss any sign-up pop-ups
        close_instagram_popups(driver)
        time.sleep(1)  # Give page a moment to settle after pop-up closes
        
        # Extract from meta description
        meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
        followers_match = re.search(r'([\d,]+)\s+Followers', meta_desc)
        following_match = re.search(r'([\d,]+)\s+Following', meta_desc)
        posts_match = re.search(r'([\d,]+)\s+Posts', meta_desc)
        
        followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
        following = int(following_match.group(1).replace(',', '')) if following_match else 0
        posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
        
        # Username features
        username = url.rstrip('/').split('/')[-1]
        username_length = len(username)
        nums_username = sum(c.isdigit() for c in username)
        nums_length_username = nums_username / username_length if username_length > 0 else 0.0
        
        # Full name
        try:
            fullname = driver.find_element(By.XPATH, "//h1 | //h2[contains(@class, 'x1lliihq')]").text.strip()
        except:
            fullname = username
        
        fullname_words = len(fullname.split())
        fullname_len = len(fullname)
        nums_fullname = sum(c.isdigit() for c in fullname)
        nums_length_fullname = nums_fullname / fullname_len if fullname_len > 0 else 0.0
        name_equals_username = 1 if fullname.lower() == username.lower() else 0
        
        # Bio/description
        try:
            bio = driver.find_element(By.XPATH, "//div[contains(@class, 'x7a106z')]//span | //div[@class='_aa_c']//span").text
            description_length = len(bio)
        except:
            description_length = 0
        
        # External URL
        external_url = 1 if driver.find_elements(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'instagram'))]") else 0
        
        # Private account
        private = 1 if driver.find_elements(By.XPATH, "//h2[contains(text(), 'This Account is Private')]") else 0
        
        # Profile picture (custom vs default)
        try:
            pic = driver.find_element(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            pic_src = pic.get_attribute("src")
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
