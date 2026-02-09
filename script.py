import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= CONFIGURATION =================
TARGET_LOCATION = "Columbia" 
# =================================================

def get_brave_driver():
    options = Options()
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    options.add_argument("--headless") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

def save_log(data, filename="scrape_log.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def scrape_coupons():
    driver = get_brave_driver()
    wait = WebDriverWait(driver, 10)
    
    log_data = {
        "session_start": time.strftime("%Y-%m-%d %H:%M:%S"),
        "search_term": TARGET_LOCATION,
        "results": {"categories_found": [], "offers_scanned": []}
    }
    
    try:
        print(f"--- TIER 1: Accessing Homepage ---")
        driver.get("https://coupons-2save.com/greatclips")
        time.sleep(3)
        
        items = driver.find_elements(By.CLASS_NAME, "com-content-category-blog__item")
        category_links = []
        
        for item in items:
            if len(item.find_elements(By.CSS_SELECTOR, ".expired")) > 0:
                continue 
            try:
                link = item.find_element(By.CSS_SELECTOR, "a[href*='/greatclips/']")
                href = link.get_attribute("href")
                if href: category_links.append(href)
            except: continue

        category_links = list(set(category_links))
        log_data["results"]["categories_found"] = category_links
        print(f"Found {len(category_links)} active deal categories.")

        all_offer_urls = []
        for cat_url in category_links:
            driver.get(cat_url)
            time.sleep(2)
            found_offers = driver.find_elements(By.XPATH, "//a[contains(@href, 'offers.greatclips.com')]")
            for offer in found_offers:
                url = offer.get_attribute("href")
                if url and url not in all_offer_urls: all_offer_urls.append(url)
        
        print(f"\n--- TIER 3: Strict Scanning for '{TARGET_LOCATION}' ---")
        matches = []
        
        # Regex setup: matches standalone word, case-insensitive
        pattern = re.compile(rf'\b{re.escape(TARGET_LOCATION)}\b', re.IGNORECASE)
        
        for i, url in enumerate(all_offer_urls):
            print(f"[{i+1}/{len(all_offer_urls)}] Checking: {url}")
            entry = {"url": url, "match": False, "raw_description": ""}
            
            try:
                driver.get(url)
                details_element = wait.until(EC.presence_of_element_located((By.ID, "offer-details")))
                time.sleep(2)
                
                full_text = details_element.text
                entry["raw_description"] = full_text
                
                # FIX: Remove the boilerplate 'All Great Clips' footer entirely before checking
                # This prevents the 'all' false positive you saw in Fresno/Saint Joseph links.
                relevant_content = full_text.split("All Great Clips")[0]
                
                # Check for the target location specifically
                if pattern.search(relevant_content):
                    print(f"    !!! VERIFIED MATCH FOUND FOR {TARGET_LOCATION}")
                    entry["match"] = True
                    matches.append(url)
                else:
                    print(f"    [-] No match for {TARGET_LOCATION}.")
            
            except Exception as e:
                print(f"    [!] ID 'offer-details' not found or timeout.")
            
            log_data["results"]["offers_scanned"].append(entry)
            save_log(log_data)

        print(f"\n--- SCRAPE FINISHED ---")
        print(f"Total Verified Matches: {len(matches)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_coupons()