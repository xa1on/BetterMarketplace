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
        #chrome_options.add_argument("--headless")
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

        id_pattern = r"(\d+)"

        found_new = []
        listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
        for listing in listings:
            try:
                url = 'https://www.facebook.com/' + listing.find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')['href']
                id = re.findall(id_pattern, url)[0]
                if not self.check_id(id):
                    self.pre_process(id, listing, url)
                    found_new.append((id, url))
            except:
                pass
        for listing in found_new:
            self.update_process(listing[0], listing[1])



    def pre_process(self, id, d, url):
        price = self.price_to_int(d.find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').text)
        title = d.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text
        location = d.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84').text
        link = url
        image = d.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')['src']
        self.store_data([id, price, title, location, link, image, "null"])

    def update_process(self, id, url): #given a data dict ({"text": (price\ntitle\nlocation\nmilage), "url": (link)}) scrape the item's page for more info
        self.browser.get(url)

        self.close_button()
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);") # scrolls the page a bit to press the See more button
        self.see_more()

        html = self.browser.page_source

        soup = BeautifulSoup(html, 'html.parser')
        description = soup.find('div', class_='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a').find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u').text.replace(" See less", "")
        self.update_desc(id, description)


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
                INSERT INTO {table_name} (id, price, title, location, link, image, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)

        except Exception as e:
            print(f"Error: {e}")
            return False

        # Commit the transaction
        self.conn.commit()
    
    def update_desc(self, id, description):
        print(description)
        self.cur.execute(f"""
            UPDATE items
            SET description = %s
            WHERE id = %s
        """, [description] + [id])
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