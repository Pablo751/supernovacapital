#!/usr/bin/env python
# coding: utf-8

# In[128]:


#

from urllib.parse import urlparse
import csv

# Declare url_list globally
url_list = []

# Function to scrape a single page
def scrape_page(url, session, visited, csv_writer, url_list):
    visited.add(url)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get the domain of the starting URL
    domain = urlparse(url).netloc
    
    # Add new URLs to the queue
    for a_tag in soup.find_all('a'):
        new_url = urljoin(url, a_tag.get('href'))
        
        # Check if the new URL is from the same domain
        new_domain = urlparse(new_url).netloc
        
        if new_domain == domain and "cdn-cgi" not in new_url and "#" not in new_url and "page" not in new_url:
            if new_url not in visited:
                print(f"Adding to queue: {new_url}")
                csv_writer.writerow([new_url])  # Write to CSV
                url_list.append(new_url)  # Add to Python list
                scrape_page(new_url, session, visited, csv_writer, url_list)

# Main function to start the scraping
def main():
    global url_list  # Declare url_list as global
    start_url = "https://www.rvingknowhow.com/"
    visited = set()
    
    # Open CSV file for writing
    with open('/Users/juanpablocasadobissone/Downloads/rvi.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["URL"])  # Write header
        
        with requests.Session() as session:
            scrape_page(start_url, session, visited, csv_writer, url_list)
    
    print("List of URLs:")

# Entry point of the script
if __name__ == "__main__":
    main()
    
print(url_list)


# In[138]:


#TM scraper
print("Script is running!")

from urllib.parse import urlparse, urljoin  # Add urljoin
import csv
import gzip  
from io import BytesIO  
import requests  # Add this import
from bs4 import BeautifulSoup  # Add this import
from gzip import BadGzipFile 

# Declare url_list globally
url_list = []

# Function to collect technical SEO data for a page
def collect_seo_data(url, soup, status_code): 
    data = {'URL': url}
        
    # Use sets to avoid duplicates.
    images_missing_alt = set()
    images_missing_alt_urls = set()  # Initialize as a set.

    
    # Collecting title tag
    title_tag = soup.find('title')
    data['Title'] = title_tag.string if title_tag else "N/A"  # <-- Note the change here
    
    # Collecting meta description
    meta_description_tag = soup.find('meta', {'name': 'description'})
    data['Meta Description'] = meta_description_tag['content'] if meta_description_tag else "N/A"  # <-- Note the change here
    
    # Collecting h1 tags
    h1_tags = [tag.string for tag in soup.find_all('h1') if tag.string]  # <-- Note the added condition
    data['H1 Tags'] = h1_tags if h1_tags else ["N/A"]  # <-- Note the change here
    
    # Collecting images missing alt text but only with http or https URLs
    for img in soup.find_all('img'):  # Note: You forgot to loop through images here.
        if not img.get('alt'):  # Check for missing alt attributes
            if not img['src'].startswith("data:"):  # Exclude data URIs
                images_missing_alt.add(img)
                images_missing_alt_urls.add(img['src'])  # Add to set
    
    # Collecting Canonical Tag
    canonical_tag = soup.find('link', {'rel': 'canonical'})
    data['Canonical Tag'] = canonical_tag['href'] if canonical_tag else "N/A"

    # Collecting Robots Meta Tag
    robots_tag = soup.find('meta', {'name': 'robots'})
    data['Robots Meta Tag'] = robots_tag['content'] if robots_tag else "N/A"

    # Collecting number of internal links
    domain = urlparse(url).netloc
    internal_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc == domain]
    data['Number of Internal Links'] = len(internal_links)

    # Collecting number of external links
    external_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc != domain]
    data['Number of External Links'] = len(external_links)

    # Collecting HTTP Status Code
    data['HTTP Status Code'] = status_code  # Add this line

    for img in soup.find_all('img', alt=True):
        if not img['alt']:
            images_missing_alt.add(img)
            if not img['src'].startswith("data:"):  # Exclude data URIs
                images_missing_alt_urls.add(img['src'])  # Add to set

            
    
# Convert sets to lists right before returning the data
    return {
        "URL": url,
        "Title": data['Title'],
        "Meta Description": data['Meta Description'],
        "H1 Tags": data['H1 Tags'],
        "Images Missing Alt": len(images_missing_alt),
        "Images Missing Alt URLs": list(images_missing_alt_urls),
        "Canonical Tag": data['Canonical Tag'],
        "Robots Meta Tag": data['Robots Meta Tag'],
        "Number of Internal Links": data['Number of Internal Links'],
        "Number of External Links": data['Number of External Links'],
        "HTTP Status Code": status_code
    }

# Function to scrape a single page
def scrape_page(url, session, visited, csv_writer, seo_csv_writer):  # Remove url_list
    print(f"Scraping: {url}")  # Add this line
    visited.add(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537',
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
    
        is_gzip = 'gzip' in response.headers.get('Content-Encoding', '')
    
        if is_gzip:
            buf = BytesIO(response.content)
            try:
                f = gzip.GzipFile(fileobj=buf)
                html = f.read().decode('utf-8')
            except BadGzipFile:  # Handle the exception here
                html = response.text  # Fallback to this if gzip decoding fails
        else:
            html = response.text
    
        soup = BeautifulSoup(html, 'html.parser')
            
         # New code to collect SEO data
        seo_data = collect_seo_data(url, soup, response.status_code)  # Pass the status_code
        
        # Join images missing alt URLs with semicolon
        images_missing_alt_urls_str = ";".join(filter(None, seo_data['Images Missing Alt URLs']))  # Get the data from seo_data

        
        seo_csv_writer.writerow([seo_data['URL'], seo_data['Title'], seo_data['Meta Description'], 
                                 ", ".join(filter(None, seo_data['H1 Tags'])), seo_data['Images Missing Alt'],
                                 images_missing_alt_urls_str, seo_data['Canonical Tag'], seo_data['Robots Meta Tag'], 
                                 seo_data['Number of Internal Links'], seo_data['Number of External Links'], 
                                 seo_data['HTTP Status Code']])

                
        # Get the domain of the starting URL
        domain = urlparse(url).netloc
    
        # Add new URLs to the queue
        for a_tag in soup.find_all('a'):
            new_url = urljoin(url, a_tag.get('href'))
            new_domain = urlparse(new_url).netloc
        
            if new_domain == domain and "cdn-cgi" not in new_url and "#" not in new_url and "page" not in new_url:
                if new_url not in visited:
                    csv_writer.writerow([new_url])  # Write to CSV
                    url_list.append(new_url)  # Add to Python list

                    
    except requests.RequestException as e:  # Fix indentation here
        print(f"An error occurred: {e}")
        return


# Main function to start the scraping
def main():  
    try:
        print("Starting the scraper.") 
        global url_list  # Declare url_list as global

        url_list.append("https://www.temperaturemaster.com/")  # Initialize the queue with the start URL
        visited = set()

        # Moved inside the try block
        with open('/Users/juanpablocasadobissone/Downloads/TMingtechreccoms.csv', 'w', newline='') as seo_csvfile:
            seo_csv_writer = csv.writer(seo_csvfile)
            seo_csv_writer.writerow(['URL', 'Title', 'Meta Description', 'H1 Tags', 'Images Missing Alt', 'Images Missing Alt URLs', 'Canonical Tag', 'Robots Meta Tag', 'Number of Internal Links', 'Number of External Links', 'HTTP Status Code'])

            with open('/Users/juanpablocasadobissone/Downloads/tm.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["URL"])  # Write header

                with requests.Session() as session:
                    while url_list:  # While there are URLs in the queue
                        current_url = url_list.pop(0)  # Dequeue a URL
                        if current_url not in visited:
                            scrape_page(current_url, session, visited, csv_writer, seo_csv_writer)  # Remove url_list
                            visited.add(current_url)  # Mark as visited

        print("Scraper finished.")
    except Exception as e:
        print(f"An error occurred in main(): {e}")

# Call the main function to run the scraper
if __name__ == "__main__":  
    main()  

print(url_list)


# In[ ]:


# Function to collect technical SEO data for a page
def collect_seo_data(url, soup):
    data = {'URL': url}
    
    # Collecting title tag
    title_tag = soup.find('title')
    data['Title'] = title_tag.string if title_tag else None
    
    # Collecting meta description
    meta_description_tag = soup.find('meta', {'name': 'description'})
    data['Meta Description'] = meta_description_tag['content'] if meta_description_tag else None
    
    # Collecting h1 tags
    h1_tags = [tag.string for tag in soup.find_all('h1')]
    data['H1 Tags'] = h1_tags
    
    # Collecting images missing alt text
    images_missing_alt = [img['src'] for img in soup.find_all('img') if not img.get('alt')]
    data['Images Missing Alt'] = images_missing_alt
    
    return data


# In[85]:


#Technical SEO check

import json
import csv

# Function to remove special characters (No changes here)
def clean_string(s):
    return s.replace("\n", "").replace("\t", "").strip()

# Your function to convert JSON to CSV
def json_to_csv(json_filepath, csv_filename):
    # Read the JSON data from file (No changes here)
    with open(json_filepath, 'r') as jsonfile:
        json_data = json.load(jsonfile)
    
    # Open the CSV file for writing (No changes here)
    with open(csv_filename, 'w', newline='') as csvfile:
        # Create a CSV writer object (No changes here)
        csv_writer = csv.writer(csvfile)
        
        # Write the header row (Added 'Images Without Alt URLs')
        seo_csv_writer.writerow(['URL', 'Title', 'Meta Description', 'H1 Tags', 'Images Missing Alt', 'Images Without Alt URLs', 'Canonical Tag', 'Robots Meta Tag', 'Number of Internal Links', 'Number of External Links'])
        
        
        # Loop through the JSON data
        for url, info in json_data.items():
            # Use .get() to fetch each value safely
            title = info.get('Title')
            meta_description = info.get('Meta Description')
            h1_tags = info.get('H1 Tags')
            images_missing_alt = info.get('Images Missing Alt')
            
            # Check whether each value exists before cleaning
            if title:
                title = clean_string(title)
            if meta_description:
                meta_description = clean_string(meta_description)
            if h1_tags:
                h1_tags = clean_string(", ".join(h1_tags))  # Assuming H1 Tags is a list
            
             # New code to concatenate image URLs
            images_missing_alt_urls = ";".join(info.get('Images Missing Alt', []))
            
            # Write the data to the CSV file (Added images_missing_alt_urls)
            csv_writer.writerow([url, title, meta_description, h1_tags, len(images_missing_alt) if images_missing_alt else 0, images_missing_alt_urls])


# Location of the JSON file (No changes here)
json_filepath = '/Users/juanpablocasadobissone/Downloads/techseoTM.json'

# Convert JSON to CSV
json_to_csv(json_filepath, '/Users/juanpablocasadobissone/Downloads/techoutput.csv')


# In[46]:


print(url_list)


# In[53]:


def fetch_page_html(url):
    try:
        response = requests.get(url, timeout=10)  # 10-second timeout
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching HTML for {url}: {e}")
        return None


def analyze_seo_elements(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Fetch title tag
    title_tag = soup.title.string if soup.title else "N/A"
    
    # Fetch meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description_content = meta_description['content'] if meta_description else "N/A"
    
    # Fetch H1 tags
    h1_tags = [tag.text for tag in soup.find_all('h1')]
    
    return {
        "Title": title_tag,
        "Meta Description": meta_description_content,
        "H1 Tags": h1_tags
    }


# Initialize GSC API client
credentials = Credentials.from_service_account_file('/Users/juanpablocasadobissone/Downloads/sc-keywords-7b51596566e6.json', scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
webmasters_service = build('webmasters', 'v3', credentials=credentials)

# Function to fetch URL Inspection data for crawl errors
# Modified fetch_url_inspection function

API_KEY = "#"  # Define your API key here


def fetch_domain_crawl_errors(site_url):
    try:
        # Define the API URL for listing crawl errors by category and platform
        api_url = f"https://www.googleapis.com/webmasters/v3/sites/{site_url}/urlCrawlErrorsCounts/query?access_token={API_KEY}"
        
        # Prepare the query payload (adjust the parameters as needed)
        query_payload = {
            "start_date" : "2023-08-23",
            "end_date" : "2023-08-27",
            "category": ["authPermissions", "manyToOneRedirect", "notFollowed", "notFound", "other", "roboted", "serverError", "soft404"],  # List of categories you are interested in
            "platform": ["mobile", "smartphoneOnly", "web"]  # List of platforms you are interested in
        }
        
        # Make the API request
        response = requests.post(api_url, json=query_payload)
        
        if response.status_code == 200:
            crawl_errors = response.json()
            return {
                "Domain Crawl Errors": crawl_errors
            }
        else:
            return {
                "Domain Crawl Errors": f"Failed to fetch data. Status code: {response.status_code}"
            }
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return {}



# Modify this function in your existing code
def fetch_page_speed_insights(url):
    API_KEY = "#"
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}"
    
    response = requests.get(pagespeed_url)
    if response.status_code != 200:
        print(f"Failed to get PageSpeed data for {url}. HTTP Status Code: {response.status_code}")
        return {"Speed Score": "N/A"}
    
    result_json = response.json()
    
    try:
        speed_score = result_json['lighthouseResult']['categories']['performance']['score']
        focus_issues = result_json['lighthouseResult']['audits']  # This is a guess; check the actual structure
    except KeyError:
        print(f"KeyError: Could not find 'lighthouseResult' in the API response for {url}.")
        return {"Speed Score": "N/A"}
    
    return {
        "Speed Score": speed_score,
        "Focus Issues": focus_issues  # Add this line
    }



# Function to find images missing alt attributes
def find_images_missing_alt(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    images_missing_alt = [img.get('src') for img in img_tags if not img.get('alt')]
    return images_missing_alt

# Modify this part of your existing code
if __name__ == "__main__":
    all_urls = url_list  # Use url_list from the first cell
    home_url = "https://www.rvingknowhow.com/"  # Replace this with your actual home URL if different
    
    all_results = {}
    
    print("Starting SEO and health check analysis...")
    
    # Run GSC and PageSpeed only on the home page
    print(f"Fetching PageSpeed and GSC data for home URL: {home_url}")
    
    home_page_speed = fetch_page_speed_insights(home_url)
    home_gsc_issues = fetch_domain_crawl_errors(home_url)
    
    for index, url in enumerate(all_urls):
        print(f"Analyzing URL {index+1} of {len(all_urls)}: {url}")
        
        html_content = fetch_page_html(url)
        if html_content is None:
            print(f"Skipping {url} due to fetch error.")
            continue
        
        print("  Fetching SEO elements...")
        seo_elements = analyze_seo_elements(html_content)
        
        print("  Checking for images missing alt attributes...")
        missing_alts = find_images_missing_alt(html_content)
        
        print("  Combining results...")
        combined_results = {
            **seo_elements,
            "Images Missing Alt": missing_alts
        }
        
        all_results[url] = combined_results


    # Check and add PageSpeed and GSC data for home URL
    print("Adding PageSpeed and GSC data for home URL to the results...")
    
    # Check if the home_url exists in all_results. If not, add it.
    if home_url not in all_results:
        print(f"{home_url} not found in results. Adding it.")
        all_results[home_url] = {}
    
    # Now add the PageSpeed data
    all_results[home_url]['PageSpeed'] = home_page_speed
    all_results[home_url]['GSC Issues'] = home_gsc_issues 
    
    print("Saving results to JSON file...")
    # Save the combined results to a JSON file
    with open('/Users/juanpablocasadobissone/Downloads/techseo.json', 'w') as f:
        json.dump(all_results, f, indent=4)

    print("Analysis complete. Results saved.")


# In[ ]:


import pandas as pd

# Set the max rows to a large number or to None for unlimited
pd.set_option('display.max_rows', None)

# Load the JSON file into a DataFrame
df = pd.read_json('/Users/juanpablocasadobissone/Downloads/techseo copy.json', orient='index')

# Display the DataFrame
df


# In[57]:


# Load the JSON file into a DataFrame if you haven't
df = pd.read_json('/Users/juanpablocasadobissone/Downloads/techseo.json', orient='index')

# Get PageSpeed score and aspects to optimize for the homepage
home_url = "https://www.rvingknowhow.com/"  # Replace with your home URL if different
home_page_data = df.loc[home_url, 'PageSpeed']

if home_page_data is not None:
    print(f"Home PageSpeed Score: {home_page_data.get('Speed Score', 'N/A')}")
    focus_issues = home_page_data.get('Focus Issues', {})
    print("Aspects to Optimize:")
    for issue, details in focus_issues.items():
        print(f"  - {issue}: {details.get('description', 'N/A')}")
else:
    print("PageSpeed data for the homepage is not available.")


# In[75]:


import requests

# Function to get detailed PageSpeed Insights
def fetch_page_speed_insights(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Your API Key from Google Cloud Console
API_KEY = "#"

# URL to check
home_url = "https://www.rvingknowhow.com/"

# Fetch detailed PageSpeed Insights using API
detailed_insights = fetch_page_speed_insights(home_url, API_KEY)

if detailed_insights:
    # Print specific files/processes that can be improved
    audits = detailed_insights.get('lighthouseResult', {}).get('audits', {})
    for audit_name, audit_data in audits.items():
        print(f"{audit_name}: {audit_data.get('title')}")
        print(f"  Description: {audit_data.get('description')}")
        print(f"  Score: {audit_data.get('score')}")
        print("  =======")
else:
    print("Failed to fetch PageSpeed Insights.")


# In[77]:


import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

print("Loading service account credentials...")
# Load the service account key JSON file.
credentials = service_account.Credentials.from_service_account_file(
    '/Users/juanpablocasadobissone/Downloads/sc-keywords-7b51596566e6.json',
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)

# Refresh the token
credentials.refresh(Request())
print("Token refreshed.")

# Now, credentials.token should contain the access token
access_token = credentials.token

def inspect_urls_with_gsc(site_url, url_list):
    results = {}
    print(f"Inspecting a total of {len(url_list)} URLs...")

    for index, url in enumerate(url_list):
        # Skip URLs that don't have an error in the existing_results
        if existing_results.get(url, {}).get("error") is None:
            print(f"Skipping URL: {url} (already successfully inspected)")
            continue
    
    for index, url in enumerate(url_list):
        print(f"Inspecting URL {index+1} of {len(url_list)}: {url}")
        
        try:
            api_url = f"https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
            headers = {"Authorization": f"Bearer {access_token}"}
            payload = {
                "inspectionUrl": url,
                "siteUrl": site_url
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                inspection_result = data.get('inspectionResult', {})
                index_status = inspection_result.get('indexStatusResult', {})
                
                results[url] = {
                    "User Canonical": index_status.get('userCanonical', "N/A"),
                    "Google Canonical": index_status.get('googleCanonical', "N/A"),
                    "Indexing State": index_status.get('indexingState', "N/A"),
                    "Last Crawl Time": index_status.get('lastCrawlTime', "N/A"),
                    "Robots Txt State": index_status.get('robotsTxtState', "N/A"),
                    "Coverage State": index_status.get('coverageState', "N/A")
                }
                print(f"Inspection complete for URL: {url}")
            else:
                results[url] = {"error": f"Failed to fetch data. Status code: {response.status_code}"}
                print(f"Failed to inspect URL: {url}. Status code: {response.status_code}")
        except Exception as e:
            results[url] = {"error": str(e)}
            print(f"An exception occurred while inspecting URL: {url}. Error: {str(e)}")
    
    print("Inspection complete for all URLs.")
    return results

print("Loading saved URLs from JSON...")
# Load URLs from your saved JSON
with open('/Users/juanpablocasadobissone/Downloads/techseo.json', 'r') as f:
    saved_data = json.load(f)
    url_list = list(saved_data.keys())

# Site URL (the domain you've verified in Google Search Console)
site_url = "https://www.rvingknowhow.com/"

print("Starting URL inspection...")
# Inspect URLs
inspection_results = inspect_urls_with_gsc(site_url, url_list)

print("Saving results to JSON...")
# Save the results back to JSON if you like
with open('/Users/juanpablocasadobissone/Downloads/techseo2.json', 'w') as f:
    json.dump(inspection_results, f, indent=4)

print("All tasks complete.")


# In[80]:


# New function definition for re-inspecting only failed URLs
def reinspect_urls_with_gsc(site_url, existing_results):
    for index, url in enumerate(existing_results.keys()):
        # Skip URLs that don't have an error in the existing_results
        if existing_results.get(url, {}).get("error") is None:
            print(f"Skipping URL: {url} (already successfully inspected)")
            continue
        
        print(f"Re-inspecting URL {index+1}: {url}")
        
        try:
            api_url = f"https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
            headers = {"Authorization": f"Bearer {access_token}"}
            payload = {
                "inspectionUrl": url,
                "siteUrl": site_url
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                inspection_result = data.get('inspectionResult', {})
                index_status = inspection_result.get('indexStatusResult', {})
                
                # Update the existing_results dictionary with new data
                existing_results[url] = {
                    "User Canonical": index_status.get('userCanonical', "N/A"),
                    "Google Canonical": index_status.get('googleCanonical', "N/A"),
                    "Indexing State": index_status.get('indexingState', "N/A"),
                    "Last Crawl Time": index_status.get('lastCrawlTime', "N/A"),
                    "Robots Txt State": index_status.get('robotsTxtState', "N/A"),
                    "Coverage State": index_status.get('coverageState', "N/A")
                }
                print(f"Re-inspection complete for URL: {url}")
            else:
                existing_results[url] = {"error": f"Failed to fetch data. Status code: {response.status_code}"}
                print(f"Failed to re-inspect URL: {url}. Status code: {response.status_code}")
        except Exception as e:
            existing_results[url] = {"error": str(e)}
            print(f"An exception occurred while re-inspecting URL: {url}. Error: {str(e)}")
    
    print("Re-inspection complete for all URLs.")

# Load existing inspection results
with open('/Users/juanpablocasadobissone/Downloads/techseo3.json', 'r') as f:
    existing_results = json.load(f)

# Re-inspect URLs and update the existing_results dictionary
reinspect_urls_with_gsc(site_url, existing_results)

# Save the updated results to a new JSON file
with open('/Users/juanpablocasadobissone/Downloads/techseo3.json', 'w') as f:
    json.dump(existing_results, f, indent=4)

print("All re-inspection tasks complete.")


# In[139]:


from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def scrape_single_page(url):
    print(f"Scraping: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        print("HTML snippet:", str(soup)[:100])
        
        # Get the domain of the starting URL
        domain = urlparse(url).netloc

        # Find and print all internal links
        internal_links = []
        for a_tag in soup.find_all('a'):
            new_url = urljoin(url, a_tag.get('href'))
            new_domain = urlparse(new_url).netloc

            print(f"Considering new URL: {new_url}")

            if new_domain == domain and "cdn-cgi" not in new_url and "#" not in new_url and "page" not in new_url:
                print(f"Adding to internal links list: {new_url}")
                internal_links.append(new_url)
        
        print("All internal links found:", internal_links)
        
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the specific URL you mentioned
    scrape_single_page("https://temperaturemaster.com/pool-liners-choosing-the-perfect-pool-liner-for-your-backyard-oasis/")


# In[146]:


#TM scraper
print("Script is running!")

from urllib.parse import urlparse, urljoin  # Add urljoin
import csv
import gzip  
from io import BytesIO  
import requests  # Add this import
from bs4 import BeautifulSoup  # Add this import
from gzip import BadGzipFile 

# Declare url_list globally
url_list = []
visited = set()  # Declare visited as a global variable


# Function to collect technical SEO data for a page
def collect_seo_data(url, soup, status_code, domain): 
    data = {'URL': url}
        
    # Use sets to avoid duplicates.
    images_missing_alt = set()
    images_missing_alt_urls = set()  # Initialize as a set.

    
    # Collecting title tag
    title_tag = soup.find('title')
    data['Title'] = title_tag.string if title_tag else "N/A"  # <-- Note the change here
    
    # Collecting meta description
    meta_description_tag = soup.find('meta', {'name': 'description'})
    data['Meta Description'] = meta_description_tag['content'] if meta_description_tag else "N/A"  # <-- Note the change here
    
    # Collecting h1 tags
    h1_tags = [tag.string for tag in soup.find_all('h1') if tag.string]  # <-- Note the added condition
    data['H1 Tags'] = h1_tags if h1_tags else ["N/A"]  # <-- Note the change here
    
    # Collecting images missing alt text but only with http or https URLs
    for img in soup.find_all('img'):  # Note: You forgot to loop through images here.
        if not img.get('alt'):  # Check for missing alt attributes
            if not img['src'].startswith("data:"):  # Exclude data URIs
                images_missing_alt.add(img)
                images_missing_alt_urls.add(img['src'])  # Add to set
    
    # Collecting Canonical Tag
    canonical_tag = soup.find('link', {'rel': 'canonical'})
    data['Canonical Tag'] = canonical_tag['href'] if canonical_tag else "N/A"

    # Collecting Robots Meta Tag
    robots_tag = soup.find('meta', {'name': 'robots'})
    data['Robots Meta Tag'] = robots_tag['content'] if robots_tag else "N/A"

    # Collecting number of internal links
    internal_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc == domain]
    data['Number of Internal Links'] = len(internal_links)

    # Collecting number of external links
    external_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc != domain]
    data['Number of External Links'] = len(external_links)

    # Collecting HTTP Status Code
    data['HTTP Status Code'] = status_code  # Add this line

    for img in soup.find_all('img', alt=True):
        if not img['alt']:
            images_missing_alt.add(img)
            if not img['src'].startswith("data:"):  # Exclude data URIs
                images_missing_alt_urls.add(img['src'])  # Add to set

            
    
# Convert sets to lists right before returning the data
    return {
        "URL": url,
        "Title": data['Title'],
        "Meta Description": data['Meta Description'],
        "H1 Tags": data['H1 Tags'],
        "Images Missing Alt": len(images_missing_alt),
        "Images Missing Alt URLs": list(images_missing_alt_urls),
        "Canonical Tag": data['Canonical Tag'],
        "Robots Meta Tag": data['Robots Meta Tag'],
        "Number of Internal Links": data['Number of Internal Links'],
        "Number of External Links": data['Number of External Links'],
        "HTTP Status Code": status_code
    }

# Function to scrape a single page
def scrape_page(url, session, csv_writer, seo_csv_writer):
    print(f"Scraping: {url}")
    visited.add(url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537',
    }
    

    domain = urlparse(url).netloc

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
    
        is_gzip = 'gzip' in response.headers.get('Content-Encoding', '')
    
        if is_gzip:
            buf = BytesIO(response.content)
            try:
                f = gzip.GzipFile(fileobj=buf)
                html = f.read().decode('utf-8')
            except BadGzipFile:  # Handle the exception here
                html = response.text  # Fallback to this if gzip decoding fails
        else:
            html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')

        # Add new URLs to the queue
        for a_tag in soup.find_all('a'):
            new_url = urljoin(url, a_tag.get('href'))
            new_domain = urlparse(new_url).netloc
                
            if (new_domain == domain or new_domain == 'www.' + domain or new_domain == domain[4:]) and "cdn-cgi" not in new_url and "#" not in new_url and "page" not in new_url:
                if new_url not in visited and new_url not in url_list:
                    print(f"Adding to queue: {new_url}")  # Debugging: Print the URL being added to the queue
                    csv_writer.writerow([new_url])
                    url_list.append(new_url)
            
         # New code to collect SEO data
        seo_data = collect_seo_data(url, soup, response.status_code, domain)  # Pass domain
        
        # Join images missing alt URLs with semicolon
        images_missing_alt_urls_str = ";".join(filter(None, seo_data['Images Missing Alt URLs']))  # Get the data from seo_data

        
        seo_csv_writer.writerow([seo_data['URL'], seo_data['Title'], seo_data['Meta Description'], 
                                 ", ".join(filter(None, seo_data['H1 Tags'])), seo_data['Images Missing Alt'],
                                 images_missing_alt_urls_str, seo_data['Canonical Tag'], seo_data['Robots Meta Tag'], 
                                 seo_data['Number of Internal Links'], seo_data['Number of External Links'], 
                                 seo_data['HTTP Status Code']])

                    
    except requests.RequestException as e:  # Fix indentation here
        print(f"An error occurred: {e}")
        return


# Main function to start the scraping
def main():
    try:
        print("Starting the scraper.")
        global url_list, visited  # Declare url_list and visited as global

        url_list.append("https://www.temperaturemaster.com/")  # Initialize the queue with the start URL
        visited = set()

        # Open the SEO CSV file
        with open('/Users/juanpablocasadobissone/Downloads/TMingtechreccoms.csv', 'w', newline='') as seo_csvfile:
            seo_csv_writer = csv.writer(seo_csvfile)
            seo_csv_writer.writerow(['URL', 'Title', 'Meta Description', 'H1 Tags', 'Images Missing Alt', 'Images Missing Alt URLs', 'Canonical Tag', 'Robots Meta Tag', 'Number of Internal Links', 'Number of External Links', 'HTTP Status Code'])

            # Open the URL CSV file
            with open('/Users/juanpablocasadobissone/Downloads/tm.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["URL"])  # Write header

                # Start the requests session
                with requests.Session() as session:
                    while url_list:  # While there are URLs in the queue
                        current_url = url_list.pop(0)  # Dequeue a URL
                        if current_url not in visited:
                            scrape_page(current_url, session, csv_writer, seo_csv_writer)  # Call scrape_page

        print("Scraper finished.")

    except Exception as e_main:  # Corrected indentation
        print(f"An error occurred in main(): {e_main}")

    print(f"Final queue: {url_list}")

# Call the main function to run the scraper
if __name__ == "__main__":
    main()


# In[155]:


import requests

# Function to get detailed PageSpeed Insights
def fetch_page_speed_insights(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Your API Key from Google Cloud Console
API_KEY = "#"

# URL to check
home_url = "https://www.rvingknowhow.com/"

# Fetch detailed PageSpeed Insights using API
detailed_insights = fetch_page_speed_insights(home_url, API_KEY)
if detailed_insights:
    # Print specific files/processes that can be improved
    audits = detailed_insights.get('lighthouseResult', {}).get('audits', {})
    for audit_name, audit_data in audits.items():
        print(f"{audit_name}: {audit_data.get('title', 'N/A')}")
        print(f"  Description: {audit_data.get('description', 'N/A')}")
        print(f"  Score: {audit_data.get('score', 'N/A')}")

        details = audit_data.get('details', {})
        items = details.get('items', [])
        
        if items:
            print("  Resources to Optimize:")
            for item in items:
                resource_info = "Unknown"

                # General case
                if isinstance(item, dict):
                    resource_info = item.get('url', item.get('request', item.get('node', 'Unknown')))
                
                # Special cases for different audits can go here. Example:
                if audit_name == 'third-party-summary' and isinstance(item, dict):
                    entity = item.get('entity', {})
                    if isinstance(entity, dict):
                        resource_info = entity.get('url', 'Unknown')
                    else:
                        resource_info = str(entity)
                
                # If item is not a dictionary, just display it as-is
                if not isinstance(item, dict):
                    resource_info = str(item)

                
                
                print(f"    - {resource_info}")
        else:
            print("  No resources to optimize.")

        print("  ========")


else:
    print("Failed to fetch PageSpeed Insights.")


# In[160]:


import requests

# Function to get detailed PageSpeed Insights
def fetch_page_speed_insights(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Your API Key from Google Cloud Console
API_KEY = "#"

# URL to check
home_url = "https://www.rvingknowhow.com/"

# Fetch detailed PageSpeed Insights using API
detailed_insights = fetch_page_speed_insights(home_url, API_KEY)
if detailed_insights:
    # Print specific files/processes that can be improved
    audits = detailed_insights.get('lighthouseResult', {}).get('audits', {})
    for audit_name, audit_data in audits.items():
        audit_title = audit_data.get('title', 'N/A')

        # Skip certain audits that don't typically provide useful information
        if audit_title in ['Server Backend Latencies', 'Tasks', 'Minimizes main-thread work', 
                           'Network Round Trip Times', 'Diagnostics', 'Cumulative Layout Shift',
                           'Final Screenshot', 'Screenshot Thumbnails']:  # Added two more titles here
            continue 

        # Skip audits that don't require optimization
        score = audit_data.get('score', 1)
        if score == 1:
            continue  # Skip to the next iteration

        print(f"{audit_name}: {audit_title}")
        print(f"  Description: {audit_data.get('description', 'N/A')}")
        print(f"  Score: {score}")

        details = audit_data.get('details', {})
        items = details.get('items', [])

        # Special handling for certain audits
        if audit_name in ['mainthread-work-breakdown', 'screenshot-thumbnails', 'metrics', 
                          'network-server-latency', 'main-thread-tasks', 'max-potential-fid', 'network-rtt']:
            if 'items' in details:
                print("  Special Resources:")
                for item in details['items']:
                    if isinstance(item, dict):
                        special_resource_info = item.get('someKey', 'Unknown')  # Adjust 'someKey' based on actual structure
                        print(f"    - {special_resource_info}")
                    else:
                        print(f"    - {item}")

        
        # General handling for 'items' in audit details
        if items:
            print("  Resources to Optimize:")
            for item in items:
                resource_info = "Unknown"

                # General case
                if isinstance(item, dict):
                    resource_info = item.get('url', item.get('request', item.get('node', 'Unknown')))
                
                # Special case for 'third-party-summary'
                if audit_name == 'third-party-summary' and isinstance(item, dict):
                    entity = item.get('entity', {})
                    if isinstance(entity, dict):
                        resource_info = entity.get('url', 'Unknown')
                    else:
                        resource_info = str(entity)
                
                # If item is not a dictionary, just display it as-is
                if not isinstance(item, dict):
                    resource_info = str(item)
                
                print(f"    - {resource_info}")
        elif audit_name not in ['mainthread-work-breakdown', 'screenshot-thumbnails', 'metrics', 
                                'network-server-latency', 'main-thread-tasks', 'max-potential-fid', 'network-rtt']:
            # If 'items' is empty and it's not one of the special cases
            print("  No resources to optimize.")  # <-- This is the line you add

        print("  ========")
else:
    print("Failed to fetch PageSpeed Insights.")


# In[170]:


from google.oauth2.service_account import Credentials
import googleapiclient.discovery
import requests

# Initialize Google Sheets API
def init_sheets_api():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = '/Users/juanpablocasadobissone/Downloads/sc-keywords-e8396be7a36c.json'

    credentials = None
    credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    return service

# Function to export data to Google Sheets
def export_to_google_sheets(service, sheet_id, audit_data):
    sheet = service.spreadsheets()
    # Prepare data for Google Sheets
    values = [["Audit Name", "Title", "Description", "Score"]]
    for audit in audit_data:
        values.append([audit['name'], audit['title'], audit['description'], audit['score']])
        
    # Write to Google Sheets
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=sheet_id, range="Sheet1!A1", body=body, valueInputOption="RAW").execute()


# Function to get detailed PageSpeed Insights
def fetch_page_speed_insights(url, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Your API Key from Google Cloud Console
API_KEY = "#"

# URL to check
home_url = "https://temperaturemaster.com/"

# Fetch detailed PageSpeed Insights using API
detailed_insights = fetch_page_speed_insights(home_url, API_KEY)
if detailed_insights:
    # Print specific files/processes that can be improved
    audits = detailed_insights.get('lighthouseResult', {}).get('audits', {})
    for audit_name, audit_data in audits.items():
        audit_title = audit_data.get('title', 'N/A')

        # Skip certain audits that don't typically provide useful information
        if audit_title in ['Server Backend Latencies', 'Tasks', 'Minimizes main-thread work', 
                           'Network Round Trip Times', 'Diagnostics', 'Cumulative Layout Shift',
                           'Final Screenshot', 'Screenshot Thumbnails']:  # Added two more titles here
            continue 

        # Skip audits that don't require optimization
        score = audit_data.get('score', 1)
        if score == 1:
            continue  # Skip to the next iteration

        print(f"{audit_name}: {audit_title}")
        print(f"  Description: {audit_data.get('description', 'N/A')}")
        print(f"  Score: {score}")

        details = audit_data.get('details', {})
        items = details.get('items', [])

        # Special handling for certain audits
        if audit_name in ['mainthread-work-breakdown', 'screenshot-thumbnails', 'metrics', 
                          'network-server-latency', 'main-thread-tasks', 'max-potential-fid', 'network-rtt']:
            if 'items' in details:
                print("  Special Resources:")
                for item in details['items']:
                    if isinstance(item, dict):
                        special_resource_info = item.get('someKey', 'Unknown')  # Adjust 'someKey' based on actual structure
                        print(f"    - {special_resource_info}")
                    else:
                        print(f"    - {item}")

        
        # General handling for 'items' in audit details
        if items:
            print("  Resources to Optimize:")
            for item in items:
                resource_info = "Unknown"

                # General case
                if isinstance(item, dict):
                    resource_info = item.get('url', item.get('request', item.get('node', 'Unknown')))
                
                # Special case for 'third-party-summary'
                if audit_name == 'third-party-summary' and isinstance(item, dict):
                    entity = item.get('entity', {})
                    if isinstance(entity, dict):
                        resource_info = entity.get('url', 'Unknown')
                    else:
                        resource_info = str(entity)
                
                # If item is not a dictionary, just display it as-is
                if not isinstance(item, dict):
                    resource_info = str(item)
                
                print(f"    - {resource_info}")
        elif audit_name not in ['mainthread-work-breakdown', 'screenshot-thumbnails', 'metrics', 
                                'network-server-latency', 'main-thread-tasks', 'max-potential-fid', 'network-rtt']:
            # If 'items' is empty and it's not one of the special cases
            print("  No resources to optimize.")  # <-- This is the line you add

        print("  ========")
else:
    print("Failed to fetch PageSpeed Insights.")


# Initialize Google Sheets API
service = init_sheets_api()  # <-- Place this line here

# Prepare data for export
audit_data_for_export = []
for audit_name, audit_data in audits.items():
    audit_title = audit_data.get('title', 'N/A')
    audit_description = audit_data.get('description', 'N/A')
    audit_score = audit_data.get('score', 'N/A')

    # Gather resources to optimize
    details = audit_data.get('details', {})
    items = details.get('items', [])
    resources_to_optimize = [item.get('url', 'Unknown') for item in items if isinstance(item, dict)]

    audit_data_for_export.append({
        'name': audit_name,
        'title': audit_title,
        'description': audit_description,
        'score': audit_score,
        'resources_to_optimize': ", ".join(resources_to_optimize)  # Convert list to comma-separated string
    })

# Function to export data to Google Sheets
def export_to_google_sheets(service, sheet_id, audit_data, sheet_name="Sheet1"):
    sheet = service.spreadsheets()
    # Prepare data for Google Sheets
    values = [["Audit Name", "Title", "Description", "Score", "Resources to Optimize"]]
    for audit in audit_data:
        values.append([audit['name'], audit['title'], audit['description'], audit['score'], audit['resources_to_optimize']])
    
    # Write to Google Sheets
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=sheet_id, 
        range=f"{sheet_name}!A1",  # Use the sheet_name parameter here
        body=body, 
        valueInputOption="RAW"
    ).execute()


# Export to Google Sheets
SHEET_ID = '1MthZNBqNFEnorFJ17RV3eF8OEozWb2dYKb9yrSIvY1o'
export_to_google_sheets(service, SHEET_ID, audit_data_for_export, sheet_name="PS TM")



# In[ ]:




