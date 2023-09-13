from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Define the function to parse related searches
def parse_related_searches(soup):
    related_searches = []
    
    # Look for both "Related searches" and "Related to this search"
    for label in ["Related searches", "Related to this search"]:
        related_div = soup.find('div', string=label, class_="oIk2Cb")
        
        if related_div:
            for div in related_div.find_all('div', recursive=False):
                span = div.find('span')
                if span:
                    related_searches.append(span.text)
                    
    return related_searches

# Define the function to find related queries
def find_related_queries(query):
    # Initialize the Chrome Service
    service = Service(executable_path='/Users/juanpablocasadobissone/Downloads/chromedriver-mac-arm64 2/chromedriver')
    
    try:
        driver = webdriver.Chrome(service=service)
        print("WebDriver initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        return
    
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)

    try:
        # Wait for the 'Related searches' section to appear
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "oIk2Cb"))
        )
        
        # Get the HTML content of the page
        html_content = driver.page_source
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Call the function to parse related searches
        related_searches = parse_related_searches(soup)
        
        print("Related Searches:")
        for search in related_searches:
            print(search)
    except Exception as e:
        print(f"Failed to find 'Related searches' section: {e}")

    # Close the browser when done
    driver.quit()

# Example usage:
query = "rv parks open year round near me"
find_related_queries(query)
