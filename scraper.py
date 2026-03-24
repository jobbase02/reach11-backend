import undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import urllib.parse
import sys
import logging

# Set up logging for the scraper module
logger = logging.getLogger(__name__)

def get_secure_driver(proxy_url):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_argument('--window-size=1920,1080')
    
    if proxy_url:
        logger.info("Initializing browser with configured residential proxy.")
        options.add_argument(f'--proxy-server={proxy_url}')
    
    options.add_argument('--headless=new') # Off for debugging, uncomment for actual cloud prod

    try:
        driver = uc.Chrome(options=options, version_main=None)
    except Exception as e:
        logger.critical(f"Failed to initialize Chrome driver: {e}")
        sys.exit(1)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


# =====================================================================
# ENGINE 1: TRADITIONAL PROFILE SCRAPER (ORIGINAL - UNTOUCHED)
# =====================================================================
def reach11_lead_engine(target, li_at, proxy_url, lead_count=3):
    driver = get_secure_driver(proxy_url)
    all_leads = []
    wait = WebDriverWait(driver, 15) 
    
    try:
        logger.info("Authenticating session via cookie injection.")
        driver.get("https://www.linkedin.com/login")
        time.sleep(2) 
        driver.add_cookie({"name": "li_at", "value": li_at})
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(4)
        
        if "checkpoint" in driver.current_url or "login" in driver.current_url:
            logger.error("Authentication failed. Session cookie may be expired or flagged.")
            return []
        
        # Keyword Injection Logic for Search URL
        keywords_str = " ".join([f'"{kw}"' for kw in target.keywords]) if target.keywords else ""
        search_query = f"{target.job_title} {target.location} {keywords_str}".strip()
        encoded_query = urllib.parse.quote(search_query)
        
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER"
        
        logger.info(f"Executing deep search query: {search_query}")
        driver.get(search_url)
        time.sleep(random.uniform(4, 6)) 
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) 
        
        profile_urls = []
        all_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'linkedin.com/in/') or contains(@href, '/in/')]")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                if href and "/in/" in href:
                    clean_url = href.split('?')[0]
                    if "linkedin.com/in/" in clean_url and clean_url not in profile_urls:
                        if not any(bad_word in clean_url for bad_word in ['/overlay/', '/edit/', '/recent-activity/']):
                            profile_urls.append(clean_url)
            except Exception:
                continue 

        logger.info(f"Search extraction complete. Found {len(profile_urls)} potential profiles.")
        if len(profile_urls) == 0: 
            return []

        # 🔥 LOGIC: Dynamic Quota Filling
        for url in profile_urls:
            # Check if we have collected enough highly relevant leads
            if len(all_leads) >= lead_count:
                logger.info(f"Successfully collected {lead_count} highly relevant leads. Stopping scrape.")
                break

            logger.info(f"Processing profile: {url}")
            try:
                driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                name_elem = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                name = name_elem.text
                
                driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(2)
                
                # Fetch Maximum 3 Posts
                driver.get(url + "/recent-activity/all/")
                time.sleep(random.uniform(3, 5))
                
                post_selectors = [".update-components-text", ".feed-shared-update-v2__description"]
                posts = []
                for selector in post_selectors:
                    post_elements = driver.find_elements(By.CLASS_NAME, selector.strip('.'))[:3]
                    posts = [p.text for p in post_elements if p.text.strip()]
                    if posts: break 

                # 1st Relevancy Filter (Must have posts)
                if not posts:
                    logger.warning(f"Skipping {name}: No recent posts found. Not relevant for outreach.")
                    continue

                # 2nd Relevancy Filter (Keyword matching in posts)
                if target.keywords:
                    is_relevant = False
                    for post in posts:
                        post_lower = post.lower()
                        # Agar target keywords mein se koi ek bhi post mein mil gaya, toh relevant hai
                        if any(kw.lower() in post_lower for kw in target.keywords):
                            is_relevant = True
                            break
                    
                    if not is_relevant:
                        logger.warning(f"Skipping {name}: Posts found, but they don't contain any target keywords.")
                        continue

                logger.info(f"✅ HIGH QUALITY LEAD CAPTURED: {name} | Posts extracted: {len(posts)}")
                
                all_leads.append({
                    "name": name,
                    "linkedin_url": url,
                    "recent_posts": posts
                })
                time.sleep(random.uniform(4, 7)) # Anti-spam delay

            except TimeoutException:
                logger.warning(f"Timeout while loading profile elements for: {url}")
                continue
            except NoSuchElementException:
                logger.warning(f"Required DOM elements missing on profile: {url}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing profile {url}: {e}")
                continue 
                
        return all_leads

    finally:
        logger.info("Closing browser session and freeing resources.")
        driver.quit()


# =====================================================================
# ENGINE 2: HIGH-INTENT POST SCRAPER (NAYA ENGINE)
# =====================================================================
def reach11_post_lead_engine(target, li_at, proxy_url, lead_count=3):
    """
    Search LinkedIn Posts natively for high buying intent,
    extract the author profiles, and verify their recent posts.
    """
    driver = get_secure_driver(proxy_url)
    all_leads = []
    wait = WebDriverWait(driver, 15) 
    
    try:
        logger.info("Starting High-Intent Post Search Engine...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(2) 
        driver.add_cookie({"name": "li_at", "value": li_at})
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(4)
        
        if "checkpoint" in driver.current_url or "login" in driver.current_url:
            logger.error("Authentication failed. Session cookie may be expired.")
            return []
        
        # 1. Formulation of Content/Post Query
        # Jo keywords array mein diye hain, wahi post mein dhoondhega.
        keywords_str = " ".join([f'"{kw}"' for kw in target.keywords]) if target.keywords else target.job_title
        search_query = f"{keywords_str} {target.location}".strip()
        encoded_query = urllib.parse.quote(search_query)
        
        # NOTICE: URL is /search/results/content/ (For Posts) not /people/
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER"
        
        logger.info(f"Hunting post authors for intent query: {search_query}")
        driver.get(search_url)
        time.sleep(random.uniform(5, 7)) 
        
        # Scroll to load multiple posts on the search page
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
        
        # 2. Extract unique author profiles from those posts
        profile_urls = []
        all_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'linkedin.com/in/') or contains(@href, '/in/')]")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                if href and "/in/" in href:
                    clean_url = href.split('?')[0]
                    # Filter out company pages, hashtags, overlays, etc.
                    if "linkedin.com/in/" in clean_url and clean_url not in profile_urls:
                        if not any(bad_word in clean_url for bad_word in ['/overlay/', '/edit/', '/recent-activity/', 'linkedin.com/company/']):
                            profile_urls.append(clean_url)
            except Exception:
                continue 

        logger.info(f"Found {len(profile_urls)} potential post authors.")
        if len(profile_urls) == 0: 
            return []

        # 3. Strict Relevancy Filtering via Profile Verification
        for url in profile_urls:
            # Check if quota is filled
            if len(all_leads) >= lead_count:
                logger.info(f"Quota filled: {lead_count} high-intent leads captured successfully.")
                break

            logger.info(f"Verifying Author Profile: {url}")
            try:
                driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                name_elem = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                name = name_elem.text
                
                driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(2)
                
                # Fetch their recent posts to ensure the keyword exists in THEIR actual feed
                driver.get(url + "/recent-activity/all/")
                time.sleep(random.uniform(3, 5))
                
                post_selectors = [".update-components-text", ".feed-shared-update-v2__description"]
                posts = []
                for selector in post_selectors:
                    post_elements = driver.find_elements(By.CLASS_NAME, selector.strip('.'))[:3]
                    posts = [p.text for p in post_elements if p.text.strip()]
                    if posts: break 

                if not posts:
                    logger.warning(f"Discarded {name}: Ghost profile (No visible posts).")
                    continue
                
                # STRICT INTENT MATCH: At least one of their 3 recent posts MUST have the keyword
                if target.keywords:
                    is_relevant = False
                    for post in posts:
                        post_lower = post.lower()
                        if any(kw.lower() in post_lower for kw in target.keywords):
                            is_relevant = True
                            break
                    
                    if not is_relevant:
                        logger.warning(f"Discarded {name}: Posts found, but intent keywords missing. False positive.")
                        continue

                # Everything verified! Add to leads.
                logger.info(f"🔥 HIGH-INTENT LEAD SECURED: {name}")
                
                all_leads.append({
                    "name": name,
                    "linkedin_url": url,
                    "recent_posts": posts
                })
                time.sleep(random.uniform(5, 8)) # Human delay anti-spam

            except TimeoutException:
                logger.warning(f"Timeout while verifying author elements for: {url}")
                continue
            except NoSuchElementException:
                logger.warning(f"Required DOM elements missing on author profile: {url}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing author {url}: {e}")
                continue 
                
        return all_leads

    finally:
        logger.info("Closing browser session and freeing resources.")
        driver.quit()