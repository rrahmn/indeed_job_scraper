from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import random
import re
import json



def launch_browser(link, options):
    """function to launch browser using provided link"""
    # Driver setup
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(link)
    return driver

def find_job_id_urls(driver):
    """function to return ids,names and urls of job listings in page"""
    # Wait for the page to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='job_']"))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, "[id^='job_']")
        ids = []
        for element in elements:
            ids.append(element.get_attribute('id'))

        urls = []
        for element in elements:
            urls.append(element.get_attribute('href'))
        
        names = [element.find_element(By.CSS_SELECTOR, "span").text for element in elements]
    except:
        return [], [], []
    return ids, urls, names


def move_next_page(driver):
    """function to open next page"""
    try:
        # Get next page link and navigate
        next_page_link = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
        link_href = next_page_link.get_attribute('href')
        driver.get(link_href)
        return True
    except:
        return False

def get_job_text(driver, urls):
    """function to get text from job listing"""

    all_texts = []
    for url in urls:
        try:
            driver.get(url)
            # Wait for the page to load.
            WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobComponent-description"))
        )
        
            # Find the job description section by its class
            try:
                job_description_section = driver.find_element(By.CLASS_NAME, "jobsearch-JobComponent-description")
                job_text = job_description_section.text
                all_texts.append(job_text)
            except Exception as e:
                print(f"Error finding job description for {url}: {e}")
                continue
        except:
            continue
    return all_texts

def random_proxy():
    """function to get random proxy"""
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    proxies = []
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped table-bordered'})
        for row in table.find_all('tr')[1:]:  
            cols = row.find_all('td')
            ip_address = cols[0].text
            port = cols[1].text
            proxies.append(f'{ip_address}:{port}')


        # Select a random proxy from the list
        if proxies:
            return random.choice(proxies[:10])
        else:
            return "No proxies found."
    else:
        return f'Failed to retrieve content, status code: {response.status_code}'
    
def set_chrome_options():
    """function to get random proxy and set it as driver proxy"""
    proxy = random_proxy()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy--server={proxy}')
    return chrome_options



def read_json_file(file_path):
    """Read and return the content of the JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
def get_existing_ids(file_path, num_ids=5):
    """Function  to read the JSON file and return the last 'num_ids' job IDs if available."""
    data = read_json_file(file_path)
    existing_ids = [item['id'] for item in data]
    return existing_ids

def append_to_json_file(file_path, new_data):
    """Append the given data to the JSON file, ensuring valid JSON structure."""
    data = read_json_file(file_path)
    data.append(new_data)  
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)  



def clean_text(text):
    """Remove or replace weird special characters in text"""
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text



def scrape(search='data+engineer', file_path='raw_database.json'):
    """Function to scrape results corresponding to search on indeed."""

    service = Service(executable_path="chromedriver.exe")
    

    chrome_options = set_chrome_options()
    driver = launch_browser(link=f"https://uk.indeed.com/jobs?q={search}&l=United+Kingdom&sort=date", options=chrome_options)
    
    next_page = True
    consecutive_existing_ids = 0  # Counter for consecutive existing job IDs
    while next_page and consecutive_existing_ids < 10:  # Allow some tolerance
        chrome_options = set_chrome_options()
        existing_ids = set(get_existing_ids(file_path)) 
        job_listing_driver = webdriver.Chrome(service=service, options=chrome_options)
        ids, urls, names = find_job_id_urls(driver)
        
        for id_, name, url, job_text in zip(ids, names, urls, get_job_text(job_listing_driver, urls)):
            if id_ in existing_ids:
                consecutive_existing_ids += 1
                if consecutive_existing_ids >= 10:  # Found 10 consecutive existing IDs, likely all subsequent jobs are already known
                    break
                continue  # Skip this job and move to the next
            else:
                consecutive_existing_ids = 0

            cleaned_job_text = clean_text(job_text)
            new_entry = {
                'id': id_,
                'search': search,
                'name': name,
                'url': url,
                'description': cleaned_job_text
            }
            append_to_json_file(file_path, new_entry)
            existing_ids.add(id_) 
        
        job_listing_driver.close()
        if consecutive_existing_ids < 10: 
            next_page = move_next_page(driver)
        else:
            break

def main():
    fields_to_scrape = [
        ('data+engineer', 'raw_database_data_engineer.json')
    ]

    for field in fields_to_scrape:
        scrape(search=field[0], file_path=field[1])

if __name__ == "__main__":
    main()
