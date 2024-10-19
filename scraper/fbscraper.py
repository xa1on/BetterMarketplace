#Import Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import psycopg2

class fbscraper():

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options = chrome_options)

        self.conn = psycopg2.connect(host = "localhost", dbname = "postgres", port = 5432)
        self.cur = self.conn.cursor()
        self.db = "cars"

    def close_button(self):
        try:
            close_button = self.browser.find_element(By.XPATH, '//div[@aria-label="Close" and @role="button"]')
            close_button.click()
            print("Close button clicked!")
            
        except:
            print("Could not find or click the close button!")
            pass

    def see_more(self):
        try:
            see_more_button = self.browser.find_element(By.XPATH, '//div[@role="button" and @tabindex="0"]//span[text()="See more"]')
            see_more_button.click()
        
        except:
            print("Could not find or click the see more button!")
            pass

    def search(self, product, city, days_listed = 1):

        # Set up base URL
        url = f'https://www.facebook.com/marketplace/{city}/search?query={product}&daysSinceListed={days_listed}&exact=false&?sortBy=creation_time_descend'

        # Visit the website
        self.browser.get(url)

        self.close_button()
    
        # Retrieve the HTML
        html = self.browser.page_source

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html, 'html.parser')


        links = soup.find_all('a')
        valid_links = [link for link in links if product.lower() in link.text.lower()]

        id_pattern = r"(\d+)"
        for valid_link in valid_links:
            url = valid_link.get('href')
            id = re.findall(id_pattern, url)[0]
            print(self.check_id(id))
            if not self.check_id(id):
                text = '\n'.join(valid_link.stripped_strings)
                d = ({'text': text, 'url': url})
                self.process_data(id, d)



    def process_data(self, id, d):
        split_input_text = re.split(r'\n', d["text"])[:-1] # we remove the first index because cars milage is last item, but we want to use more accurate milage??
        # maybe we don't do this because its harder to do both regular items and cars

        split_input_text[0] = self.price_to_int(split_input_text[0])

        new_url = d["url"]
        self.browser.get(f"https://facebook.com{new_url}")

        self.close_button()
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);")
        self.see_more()


        html = self.browser.page_source

        soup = BeautifulSoup(html, 'html.parser')

        data = soup.get_text()
        data = ' '.join(data.splitlines())

        miles_pattern = r"Driven ([\d,]+).+miles"
        transmission_pattern = r"([A-Z][a-z]+) transmission"
        color_pattern = r"color: ([a-zA-Z]+)"
        location_pattern = r"Location(\S+)[, ]"
        location = re.findall(location_pattern, data)[0]
        description_pattern = rf"Seller's description(.+){location}[, ]"
        patterns = [miles_pattern, transmission_pattern, color_pattern, description_pattern]
        
        for p in patterns:
            split_input_text.append(re.findall(p, data)[0])
        
        split_input_text[3] = self.price_to_int(split_input_text[3])

        data_to_store = tuple([id] + split_input_text)
        self.store_data(data_to_store)

    def check_id(self, id, table_name = "cars", column_name = "id"):
        try:
            self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column_name} = CAST({id} AS varchar) LIMIT 1)")
            
            exists = self.cur.fetchone()[0]

            return exists

        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def store_data(self, data, table_name="cars"):
        print(data)
        try:
            # Use parameterized query to avoid SQL injection and handle special characters
            self.cur.execute(f"""
                INSERT INTO {table_name} (id, price, title, location, miles, transmission, color, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data)

        except Exception as e:
            print(f"Error: {e}")
            return False

        # Commit the transaction
        self.conn.commit()

        
    def price_to_int(self, price_str):

        cleaned_price = price_str.replace('$', '').replace(',', '')
        
        try:
            return int(cleaned_price)
        except ValueError:
            print(f"Error: Unable to convert '{price_str}' to an integer.")
            return None
    

if __name__ == "__main__":
    scraper = fbscraper()
    scraper.search("brz", "sanjose")