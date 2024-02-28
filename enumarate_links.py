import sys
import requests
import time
import random
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

class LinkEnumeration:
    def __init__(self, rate_limit=False, random_delay=False, num_threads=2, num_processes=2):
        self.rate_limit = rate_limit
        self.random_delay = random_delay
        self.num_threads = num_threads
        self.num_processes = num_processes
        self.user_agents = [
            # User agent strings
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.3",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (X11; Linux i686; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 
            'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; SM-A127M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; HD1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36' 
        ]
    
    def send_request(self, url):
        headers = {'User-Agent': random.choice(self.user_agents)}
        if self.rate_limit:
            time.sleep(1)  # Rate limit by 1 second
        if self.random_delay:
            time.sleep(random.uniform(0.5, 3))  # Random delay between 0.5 and 3 seconds
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print("Error fetching page:", e)
            return None

    def get_links(self, url):
        html_content = self.send_request(url)
        if html_content:
            links = []
            for link in html_content.split('href="')[1:]:
                link = link.split('"')[0]
                if link.startswith("http"):
                    links.append(link)
                elif link.startswith("/"):
                    links.append(url + link)
            return links
        else:
            return []

    def crawl_website(self, start_url, depth=4):
        visited = set()
        queue = [(start_url, 0)]
        all_links = set()
        
        def process_url(url, level):
            if url not in visited:
                visited.add(url)
                if level <= depth:
                    links = self.get_links(url)
                    all_links.update(links)
                    for link in links:
                        queue.append((link, level + 1))

        # Multithreading using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            while queue:
                url, level = queue.pop(0)
                executor.submit(process_url, url, level)
        
        return all_links

    def save_to_file(self, links, file_path):
        with open(file_path, "w") as file:
            for link in links:
                file.write(link + "\n")

if __name__ == "__main__":
    # Default URL
    default_url = "https://www.microsoft.com/"

    # Use default URL if no URL provided as argument
    start_url = sys.argv[1] if len(sys.argv) > 1 else default_url

    # Derive file name from domain of the URL
    domain = urlparse(start_url).netloc
    file_path = f"C:\\Users\\user\OneDrive\\NetworkAuditing-and-ExplorationTool\\enumerated_links\\{domain}_links.txt"

    # Example usage:
    link_enumerator = LinkEnumeration(rate_limit=False, random_delay=False)
    all_links = link_enumerator.crawl_website(start_url, depth=4)
    link_enumerator.save_to_file(all_links, file_path)
    print("All links have been saved to:", file_path)
