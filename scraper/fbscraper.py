#Import Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import psycopg2

class fbscraper():

    def __init__(self): # creates browser object for scraping, as well as connecting to db
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options = chrome_options)

        self.conn = psycopg2.connect(host = "localhost", dbname = "postgres", port = 5432)
        self.cur = self.conn.cursor()
        self.db = "cars"

    def close_button(self): # helper function for closing fb buttons
        try:
            close_button = self.browser.find_element(By.XPATH, '//div[@aria-label="Close" and @role="button"]')
            close_button.click()
            print("Close button clicked!")
            
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
        for valid_link in valid_links:
            url = valid_link.get('href')
            id = re.findall(id_pattern, url)[0]
            print(self.check_id(id))
            if not self.check_id(id):
                text = '\n'.join(valid_link.stripped_strings)
                d = ({'text': text, 'url': url})
                self.process_data(id, d)



    def process_data(self, id, d): #given a data dict ({"text": (price\ntitle\nlocation\nmilage), "url": (link)}) scrape the item's page for more info
        split_input_text = re.split(r'\n', d["text"])[:-1] # we remove the first index because cars milage is last item, but we want to use more accurate milage??
        # maybe we don't do this because its harder to do both regular items and cars, so don't get the more accurate milage from the page

        split_input_text[0] = self.price_to_int(split_input_text[0]) #takes first value and converts it to integer. check if this works for normal marketplace items

        new_url = d["url"]
        self.browser.get(f"https://facebook.com{new_url}")

        self.close_button()
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);") # scrolls the page a bit to press the See more button
        self.see_more()


        html = self.browser.page_source

        soup = BeautifulSoup(html, 'html.parser')

        data = soup.get_text()
        data = ' '.join(data.splitlines())

        miles_pattern = r"Driven ([\d,]+).+miles" #all of these regex patterns are specific to the case of cars, we need to write different patterns for cars/regular items
        transmission_pattern = r"([A-Z][a-z]+) transmission"
        color_pattern = r"color: ([a-zA-Z]+)"
        location_pattern = r"Location(\S+)[, ]"
        location = re.findall(location_pattern, data)[0]
        description_pattern = rf"Seller's description(.+){location}[, ]" # we use the location here to find an end for the description
        patterns = [miles_pattern, transmission_pattern, color_pattern, description_pattern]
        
        for p in patterns:
            split_input_text.append(re.findall(p, data)[0]) # only get the first result from re.findall
        
        split_input_text[3] = self.price_to_int(split_input_text[3]) #this value is assumed to be miles, so we convert to integer

        data_to_store = tuple([id] + split_input_text)
        self.store_data(data_to_store)

    def check_id(self, id, table_name = "cars", column_name = "id"): # table name hardcoded, probably change
        try:
            self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column_name} = CAST({id} AS varchar) LIMIT 1)")
            
            exists = self.cur.fetchone()[0]

            return exists

        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def store_data(self, data, table_name="cars"): # also use case specific, tables of different objects will have different columns
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

# comments from eugene: this is extremely hard coded for cars on fb marketplace
#