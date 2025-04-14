import re
import time
import json
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global scraping configurations
retries = 2
search_posts = 30  # number of tweets need to scrape
search_keyword = "Sharekhan"
instagram_username = "varunbranco"
instagram_password = "yagyabranco"

# Setup Selenium configurations
def selenium_config():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    # options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    return browser

def retry_extraction(func, attempts=1, delay=1, default=""):
    """
    Helper function that retries an extraction function up to 'attempts' times.
    Returns the result if successful, otherwise returns 'default'.
    """
    for i in range(attempts):
        try:
            result = func()
            if result:
                return result
        except Exception:
            time.sleep(delay)
    return default

def instagram_login(browser):
    try:
        browser.get('https://www.instagram.com/accounts/login/')
        WebDriverWait(browser,20).until(
            lambda d: d.execute_script('return document.readyState')== 'complete'
        )
        # Instagram username
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR , 'input[name="username"]'))
        )
        usernameField = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR , 'input[name="username"]'))
        )
        usernameField.clear()
        usernameField.send_keys(instagram_username)
        # Instagram password
        passwordField = WebDriverWait(browser,10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR , 'input[name="password"]'))
        )
        passwordField.clear()
        passwordField.send_keys(instagram_password)
        instagram_login_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
        )
        instagram_login_button.click()
        time.sleep(2)
        return True
    except Exception as e:
        print("Login failed", e)
        return False
    
    
def save_profile_data(profile_json_data):
    try:
        os.makedirs("output", exist_ok=True)
        username = profile_json_data.get("username") or "unknown"
        filename = f"output/{username}.json"
        print(f"Saving to: {os.path.abspath(filename)}")  # Debug print
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(profile_json_data, f, indent=4, ensure_ascii=False)
        print(f"[✔] Saved profile: {username}")
        return True
    except Exception as e:
        print(f"[✘] Failed to save JSON: {e}")
        return False

def get_instagram_post(browser, post_link):
    pass

def get_instagram_profile(browser, profile_link):
    try:
        browser.execute_script("window.open('');")
        browser.switch_to.window(browser.window_handles[-1])
        browser.get(profile_link)
        WebDriverWait(browser, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(4)
        
        profile_json_data = {
            "url": profile_link,
            "username": "",
            "status": False,
            "profile_image": "",
            "total_posts": None,
            "followers": None,
            "following": None,
            "name": "",
            "threads_id": "",
            "bio": "",
         #   "links": [],
          # "posts": [],
           # "reels": [],
            #"tagged": []
        }
        instagram_profile_page = BeautifulSoup(browser.page_source, "html.parser")
        if instagram_profile_page:
            # Extracting username and status
            username_status_container_section = instagram_profile_page.find("section", {"class": "x1xdureb x1agbcgv xieb3on x1lhsz42 xr1yuqi x6ikm8r x10wlt62 xs5motx"})
            if username_status_container_section:
                # Extracting username
                try:
                    username_container = username_status_container_section.find("span", {"class":"x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft"})
                    if username_container:
                        username = username_container.get_text(strip=True)
                        if username:
                            profile_json_data["username"] = username
                except Exception as e:
                    print(f"Error extracting username: ", e)

                # Extracting status
                try:
                    status_container = username_status_container_section.find("div", {"class": "x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1gslohp x1i64zmx x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh xl56j7k"})
                    if status_container:
                        profile_json_data["status"] = True
                except Exception as e:
                    print(f"Error extracting status: ", e)
            
            # Extracting profile image
            try:
                profile_image_conatiner = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//img[contains(@alt, 'profile picture')]"))
                )
                if profile_image_conatiner:
                    profile_image = profile_image_conatiner.get_attribute("src")
                    if profile_image:
                        profile_json_data["profile_image"] = profile_image
            except Exception as e:
                print(f"Error extracting profile image: ", e)
            
            # Extracting total posts, followers and followings
            totalposts_followers_following_container_section = instagram_profile_page.find("section", {"class": "xc3tme8 x1xdureb x18wylqe x13vxnyz xvxrpd7"})
            if totalposts_followers_following_container_section:
                totalposts_followers_following_container = totalposts_followers_following_container_section.find_all("li", {"class": "xl565be x1m39q7l x1uw6ca5 x2pgyrj"})
                if totalposts_followers_following_container:
                    # Extacting total post
                    totalposts_container = totalposts_followers_following_container[0].get_text(strip=True)
                    totalposts = int(re.sub(r'\D', '', totalposts_container))
                    profile_json_data["total_posts"] = totalposts
                    # Extracting followers
                    
                    
                    
                    def parse_count_with_suffix(count_text):
                     count_text = count_text.lower()
                     if 'k' in count_text:
                         return int(float(count_text.replace('k', '')) * 1000)
                     elif 'm' in count_text:
                         return int(float(count_text.replace('m', '')) * 1000000)
                     else:
                         return int(re.sub(r'\D', '', count_text))
                    
                    
                    
                    
                    
                    
                    
                    
                    followers_container = totalposts_followers_following_container[1].get_text(strip=True)
                    followers = parse_count_with_suffix(re.search(r'[\d,.]+[KkMm]?', followers_container).group(0))
                    profile_json_data["followers"] = followers
                    # Extracting followings
                    following_container = totalposts_followers_following_container[2].get_text(strip=True)
                    following = int(re.sub(r'\D', '', following_container))  # Fixed bug here - was using followers_container
                    profile_json_data["following"] = following
            
            # Extracting name
            try:
                name_container = instagram_profile_page.find("span", {"class":"x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"})
                if name_container:
                    name = name_container.get_text(strip=True)
                    profile_json_data["name"] = name
            except Exception as e:
                print(f"Error extracting name: ", e)

            # Extracting threads id 
            try:
                threads_id_container = instagram_profile_page.find("span", {"class": "x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye x1fhwpqd xo1l8bm x5n08af x1s3etm8 x676frb x10wh9bi x1wdrske x8viiok x18hxmgj"})
                if threads_id_container:
                    threads_id = threads_id_container.get_text(strip=True)
                    profile_json_data["threads_id"] = threads_id
            except Exception as e:
                print(f"Error extracting treads id: ", e)

            # Extracting bio
            try:
                bio_container = instagram_profile_page.find("span", {"class": "_ap3a _aaco _aacu _aacx _aad7 _aade"})
                if bio_container:
                    bio = bio_container.get_text(strip=True)
                    profile_json_data["bio"] = bio
            except Exception as e:
                print(f"Error extracting bio: ", e)

            # Extracting links
            try:
                links_element_container = instagram_profile_page.find("div", {"class": "x3nfvp2.x193iq5w"})
                if links_element_container:
                    first_link_conatiner = links_element_container.find("div", {"class": "_ap3a.aaco.aacw.aacz.aada._aade"})
                    if first_link_conatiner:
                        links_element_containers = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.x3nfvp2.x193iq5w"))
                        )
                        links_button = WebDriverWait(links_element_containers, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.x1hwekxz.xyqdw3p"))
                        )
                        if links_button:
                            links_button.click()
                            time.sleep(2)
                            main_links_container = WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.x1n2onr6.xzkaem6"))
                            )
                            all_links = main_links_container.find_elements(By.TAG_NAME, "a")
                            for link in all_links:
                                href = link.get_attribute('href')
                                if href:
                                    profile_json_data["links"].append(href)
                            links_close_button = main_links_container.find_element(By.XPATH, "//*[local-name()='svg' and @aria-label='Close']")
                            if links_close_button:
                                links_close_button.click()
                                time.sleep(1)
                    else:
                        first_link_conatiner = links_element_container.find("span", {"class": "x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft"})
                        if first_link_conatiner:
                            first_link = first_link_conatiner.get_text(strip=True)
                            profile_json_data["links"].append(first_link)
            except Exception as e:
                print(f"Error extracting links: ", e)

            # Extracting posts 
            try:
                pass
            except Exception as e:
                print(f"Error extracting instagram profile posts: ", e)

        # Save the profile data to JSON before returning
        save_profile_data(profile_json_data)
        return profile_json_data
    except Exception as e:
        print(f"Error scrapping profile {profile_link}:", e)
        return False
    finally:
        browser.close()
        browser.switch_to.window(browser.window_handles[0])

def instagram_public_profile(browser, search_keyword):
    try:
        # List to store all scraped profile data
        all_profiles = []
        
        instagram_search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[local-name()="svg" and @aria-label="Search"]'))
        )
        if instagram_search_button:
            instagram_search_button.click()
            time.sleep(1)
            instagram_search_input = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR , 'input[placeholder="Search"]'))
            )
            instagram_search_input.clear()
            instagram_search_input.send_keys(search_keyword)
            time.sleep(2)
            public_profiles_container = browser.find_element(
                By.CSS_SELECTOR, "div.x6s0dn4.x78zum5.xdt5ytf.x5yr21d.x1odjw0f.x1n2onr6.xh8yej3"
            )
            if public_profiles_container:
                public_profiles_elements = public_profiles_container.find_elements(
                    By.CSS_SELECTOR, "a.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x1dm5mii.x16mil14.xiojian.x1yutycm.x1lliihq.x193iq5w.xh8yej3"
                )
                
                # Store all profile links to process
                profile_links = []
                for public_profile_element in public_profiles_elements:
                    public_profile_link = public_profile_element.get_attribute('href')
                    if public_profile_link:
                        profile_links.append(public_profile_link)
                
                print(f"Found {len(profile_links)} profiles matching '{search_keyword}'")
                
                # Process each profile
                for i, profile_link in enumerate(profile_links):
                    print(f"Processing profile {i+1}/{len(profile_links)}: {profile_link}")
                    profile_data = get_instagram_profile(browser, profile_link)
                    if profile_data and profile_data is not False:
                        all_profiles.append(profile_data)
                
                # Save all profiles as a collection to a single JSON file
                if all_profiles:
                    os.makedirs("output", exist_ok=True)
                    collection_filename = f"output/instagram_profiles_{search_keyword}_{int(time.time())}.json"
                    with open(collection_filename, "w", encoding="utf-8") as f:
                        json.dump({
                            "search_keyword": search_keyword,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "total_profiles": len(all_profiles),
                            "profiles": all_profiles
                        }, f, indent=4, ensure_ascii=False)
                    print(f"[✔] Saved all {len(all_profiles)} profiles to {collection_filename}")
                        
            time.sleep(2)
            return True
    except Exception as e:
        print("Public Profile scrapping failed: ", e)
        return False

def scrape_instagram_data():
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    print(f"Output directory created at {os.path.abspath('output')}")
    
    # selenium browser activate
    browser = selenium_config()
    try:
        # login to Instagram
        if not retry_extraction(lambda: instagram_login(browser), attempts=3, delay=2):
            print("Failed to login to Instagram after multiple attempts")
            return
        
        # scrape instagram public profiles
        retry_extraction(
            lambda: instagram_public_profile(browser, search_keyword), attempts=2, delay=2
        )
        
        print("Scraping completed successfully!")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        browser.quit()
        print("Browser closed.")

if __name__ == "__main__":
    print("=" * 50)
    print("Instagram Profile Scraper")
    print("=" * 50)
    print(f"Search keyword: {search_keyword}")
    print(f"Data will be saved to the 'output' directory")
    print("=" * 50)
    scrape_instagram_data()