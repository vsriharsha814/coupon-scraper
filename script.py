import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= CONFIGURATION =================
TARGET_LOCATION = "Boulder" 
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
        print(f"--- TIER 1: Accessing Homepage (Filtering Expired) ---")
        driver.get("https://coupons-2save.com/greatclips")
        time.sleep(3)
        
        # Scans for non-expired items based on your inspection screenshot
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
        print(f"Found {len(category_links)} active deal categories.")

        all_offer_urls = []
        for cat_url in category_links:
            driver.get(cat_url)
            time.sleep(2)
            found_offers = driver.find_elements(By.XPATH, "//a[contains(@href, 'offers.greatclips.com')]")
            for offer in found_offers:
                url = offer.get_attribute("href")
                if url and url not in all_offer_urls: all_offer_urls.append(url)
        
        print(f"\n--- TIER 3: Diagnostic Scan ---")
        matches = []
        for i, url in enumerate(all_offer_urls):
            print(f"\n[{i+1}/{len(all_offer_urls)}] Checking: {url}")
            entry = {"url": url, "match": False, "raw_description": ""}
            
            try:
                driver.get(url)
                # Targeting the ID you identified in the browser inspector
                details_element = wait.until(EC.presence_of_element_located((By.ID, "offer-details")))
                time.sleep(2)
                
                # Capture the full text to debug the false positive
                full_text = details_element.text
                entry["raw_description"] = full_text
                
                lowered_text = full_text.lower()
                search_term = TARGET_LOCATION.lower()
                
                print(f"    DEBUG TEXT FOUND: \"{full_text[:150].strip()}...\"")
                
                if search_term in lowered_text or "all" in lowered_text:
                    # Logic to ensure the location is actually in the 'valid at' sentence
                    # and not just a footer link or related salon address
                    if any(key in lowered_text for key in ["valid", "participating", "salons"]):
                        print(f"    !!! VERIFIED MATCH for {TARGET_LOCATION}")
                        entry["match"] = True
                        matches.append(url)
                else:
                    print(f"    [-] No match for {TARGET_LOCATION}.")
            
            except Exception as e:
                print(f"    [!] Details ID not found or error: {str(e)[:50]}")
            
            log_data["results"]["offers_scanned"].append(entry)
            save_log(log_data)

        print(f"\n--- FINISHED ---")
        print(f"Total Matches: {len(matches)}")
        print(f"Check 'scrape_log.json' to see the 'raw_description' for every link.")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_coupons()