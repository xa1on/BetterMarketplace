#Import Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import psycopg2
from os import environ
from dotenv import load_dotenv

load_dotenv()

sqlpass = environ["sqlpass"]

class fbscraper():

    def __init__(self): # creates browser object for scraping, as well as connecting to db
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options = chrome_options)

        self.conn = psycopg2.connect(host = "localhost", dbname = "postgres", port = 5432, password = sqlpass, user = "postgres") # also fix this database, this is eugenes on his local computer
        self.cur = self.conn.cursor()
        self.db = "items"

    def close_button(self): # helper function for closing fb buttons
        try:
            close_button = self.browser.find_element(By.XPATH, '//div[@aria-label="Close" and @role="button"]')
            close_button.click()
            # print("Close button clicked!")
            
        except:
            print("Could not find or click the close button!")
            pass

    def see_more(self): # helper function for clicking "See more" on marketplace descriptions
        try:
            see_more_button = self.browser.find_element(By.XPATH, '//div[@role="button" and @tabindex="0"]//span[text()="See more"]')
            see_more_button.click()
        
        except:
            print("Could not find or click the see more button!")
            pass

    def search(self, product, city, days_listed = 1): # given a product, city, and days listed get the data (price, title, location, milage, transmission, milage, description) of product and add to DB if it hasn't been seen before
        # we use the unique url provided by facebook
        # this should be a generic function
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

        found_new = []

        for valid_link in valid_links:
            url = valid_link.get('href')
            id = re.findall(id_pattern, url)[0]
            if not self.check_id(id):
                text = '\n'.join(valid_link.stripped_strings)
                d = ({'text': text, 'url': url})
                self.pre_process(id, d)
                found_new.append((id, d))
        for new in found_new:
            self.update_data(new[0], new[1])



    def pre_process(self, id, d):
        output = re.split(r'\n', d["text"])
        if output[1][0] == "$": # sometimes a second price shows up if its "on sale" this price isn't really important so it gets removed
            output.pop(1)
        output = output[:3] # only need the first 3, price, title, and location
        output[0] = self.price_to_int(output[0])
        self.store_data([id] + output + ["null", "null", "null"])

    def update_data(self, id, d): #given a data dict ({"text": (price\ntitle\nlocation\nmilage), "url": (link)}) scrape the item's page for more info
        new_url = d["url"]
        link = f"https://facebook.com{new_url}"
        self.browser.get(link)

        self.close_button()
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);") # scrolls the page a bit to press the See more button
        self.see_more()

        html = self.browser.page_source

        soup = BeautifulSoup(html, 'html.parser')

        data = soup.get_text(separator="\n")
        
        print(data)

    def check_id(self, id, table_name = "items", column_name = "id"): # table name hardcoded, probably change
        try:
            self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column_name} = CAST({id} AS varchar) LIMIT 1)")
            
            exists = self.cur.fetchone()[0]

            return exists

        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def store_data(self, data, table_name="items"): # also use case specific, tables of different objects will have different columns
        print(data)
        try:
            # Use parameterized query to avoid SQL injection and handle special characters
            self.cur.execute(f"""
                INSERT INTO {table_name} (id, price, title, location, description, link, image) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)

        except Exception as e:
            print(f"Error: {e}")
            return False

        # Commit the transaction
        self.conn.commit()

        
    def price_to_int(self, price_str): #helper function

        cleaned_price = price_str.replace('$', '').replace(',', '')
        
        try:
            return int(cleaned_price)
        except ValueError:
            print(f"Error: Unable to convert '{price_str}' to an integer.")
            return None
    

if __name__ == "__main__":
    scraper = fbscraper()
    scraper.search("brz", "sanjose") # searches for brz's within san jose and commits to DB

# comments from eugene: this is extremely hard coded for items on fb marketplace
# need to add images, you can probably pull the image links from the facebook data so we don't need to store images in the storage
# also look into singlestore so we don't have to deal with this garbage