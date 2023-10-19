from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
import os
import json
import time

# import ublock origin to block any popups
chrome_options = Options()
chrome_options.add_argument('load-extension=ublock_origin_1.52.2_4')

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(30)

if os.path.isfile("metadata.jsonl"):
    with open("metadata.jsonl", "r") as output_file:
        start_i = len(output_file.readlines())
    output_file = open("metadata.jsonl", "a")
else:
    start_i = 0
    output_file = open("metadata.jsonl", "w+")

for year in range(2015, 2024):
    print(f"year = {year}")

    driver.get(f"https://podcast.rthk.hk/podcast/item.php?pid=336&year={year}&list=1&lang=zh-CN")
    time.sleep(2)

    # refresh page to active ublock origin
    driver.refresh()
    time.sleep(2)

    try:
        load_all_button = driver.find_element(by=By.CSS_SELECTOR, value="button#load-all")
        load_all_button.click()
        time.sleep(5)
    except ElementNotInteractableException:
        print("No need to click load all")
    except ElementClickInterceptedException:
        # Click away the cookie consent banner first
        driver.find_element(by=By.CSS_SELECTOR, value="a.cc-btn.cc-dismiss").click()
        time.sleep(1)
        load_all_button = driver.find_element(by=By.CSS_SELECTOR, value="button#load-all")
        load_all_button.click()
        time.sleep(5)

    episode_items_path = "div.epi-item"
    episode_items = driver.find_elements(by=By.CSS_SELECTOR, value=episode_items_path)
    
    num_episodes = len(episode_items)

    for i in range(num_episodes):
        scraped_item = {}

        link = episode_items[i].find_element(by=By.CSS_SELECTOR, value="a")
        scraped_item["view_more_link"] = link.get_attribute("href")
        scraped_item["title"] = link.find_element(by=By.CSS_SELECTOR, value="div.item-desc").text
        scraped_item["date"] = link.find_element(by=By.CSS_SELECTOR, value="div.item-date").text

        try:
            link.click()
            time.sleep(2)
        except ElementClickInterceptedException:
            try:
                # Click away the cookie consent banner first
                driver.find_element(by=By.CSS_SELECTOR, value="a.cc-btn.cc-dismiss").click()
                time.sleep(1)
            except:
                pass
            link.click()
            time.sleep(2)

        download_button = driver.find_element(by=By.CSS_SELECTOR, value="a.darkBtn.icon-download")
        scraped_item["download_link"] = download_button.get_attribute("href")

        output_file.write(json.dumps(scraped_item, ensure_ascii=False) + "\n")
        output_file.flush()

        # Update the list of episode items to avoid stale elements
        episode_items_path = "div.epi-item"
        episode_items = driver.find_elements(by=By.CSS_SELECTOR, value=episode_items_path)

output_file.close()
