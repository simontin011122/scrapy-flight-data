import scrapy
from flightscraper.items import FlightscraperItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from scrapy.utils.response import open_in_browser
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.http import TextResponse
import time
# from scrapy.utils.response import debug

class SkyscannerSpider(scrapy.Spider):
    name = "hkexpress"
    def __init__(self):
        self.driver = None  # Initialize the driver attribute
    
    def wait_load_element_disappear(self, appear=True):
        while True:
            load_element = self.wait().until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.loader_message')))
            print(load_element)
            if appear:
                if load_element == True:
                    break
            else: 
                if load_element != True:
                    break    
            time.sleep(0.5)
    
    def wait(self):
        # Set the maximum waiting time in seconds
        max_wait_time = 100
        # Wait until the element with CSS selector 'flight' appears
        return WebDriverWait(self.driver, max_wait_time)
        
    def start_requests(self):
        service = Service()
        # options = webdriver.ChromeOptions()
        options = Options()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.get("https://booking.hkexpress.com/en-US/")
        
        
        # first time
        one_way = WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#HkeSearchModule-Search-TripSelector > div > div.input-group-wrap > div:nth-child(1) > label > span"))
            )
        one_way.click()
        
        self.driver.find_element(By.CSS_SELECTOR,"div.station-input-control").click()
        self.driver.find_elements(By.CSS_SELECTOR, '#HkeSearchModule-Search-RouteSelector1 > div > div.open > div.dropdownModal > div > div > div > p > a')[0].click()

        self.driver.find_elements(By.CSS_SELECTOR, '#HkeSearchModule-Search-RouteSelector1 > div > div.open > div.dropdownModal > div > div > div > p > a')[0].click()

        self.driver.find_element(By.CSS_SELECTOR, "td.today.available").click()
        self.driver.find_element(By.CSS_SELECTOR, "#HkeSearchModule-Search-FindFlightsBtn > button").click()
        
        # # bot
        # iframe = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "iframe#sec-cpt-if")))
        # driver.switch_to.frame(iframe)
        # driver.find_element(By.CSS_SELECTOR, '#robot-checkbox').click()
        # driver.find_element(By.CSS_SELECTOR, 'span#proceed-message').click()

        # driver.switch_to.default_content()
        self.wait_load_element_disappear(appear=False)
            
                
        for i in range(30): # 30 days
            self.wait_load_element_disappear()
            print("Loading disappear")
            
            # check current day info 
            all_dates = self.driver.find_elements(By.CSS_SELECTOR, 'li.slide')
            current_date = self.driver.find_element(By.CSS_SELECTOR, 'li.slide.selected')
            current_date_index = all_dates.index(current_date)
            
            # scrape data
            self.parse(current_date)
            
            # click the next page
            if len(all_dates) == current_date_index + 1:
                    self.driver.find_element(By.CSS_SELECTOR, 'button.slider_control_btn.next').click()
                    self.wait_load_element_disappear()
                    first_date = self.wait().until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.ng-star-inserted')))
                    first_date.click()
            else: 
                all_dates[current_date_index + 1].click()
        
        self.wait_load_element_disappear()
        self.driver.find_element(By.CSS_SELECTOR, 'button.button.btn-inverse').click()
        
        
    def parse(self, current_date):
        flight_elements = self.driver.find_elements(By.CSS_SELECTOR, '.flights')
        
        print("Flight elements", flight_elements)
        
        if flight_elements[0].text != 'No flights available':
            flight_date = current_date.find_element(By.CSS_SELECTOR, 'button > div > span.dayselector_date > span.date').text
            print(flight_date)
            # start scraping
            for flight_block in flight_elements:
                print("Flight block", flight_block)
                departure_col = flight_block.find_element(By.CSS_SELECTOR, '.colDeparture')
                flight_info_block = flight_block.find_element(By.CSS_SELECTOR, '.colDuration')
                arrival_col = flight_block.find_element(By.CSS_SELECTOR, '.colReturn')
                try:
                    promotion = flight_block.find_element(By.CSS_SELECTOR, '.promo-label-content').text
                except: 
                    promotion = None
                    
                item = FlightscraperItem()
                item['Date'] = flight_date
                item['DepartureTime'] = departure_col.find_element(By.CSS_SELECTOR, 'span.time').text
                item['DepartureAirport'] = departure_col.find_element(By.CSS_SELECTOR, 'span.airport-city').text
                item['FlightDuration'] = flight_info_block.find_element(By.CSS_SELECTOR, '.time').text.split("\n")[1]
                item['FlightNumber'] = flight_info_block.find_element(By.CSS_SELECTOR, '.flight-number').text
                item['ArrivalTime'] = arrival_col.find_element(By.CSS_SELECTOR, 'span.time').text
                item['ArrivalAirport'] = arrival_col.find_element(By.CSS_SELECTOR, 'span.airport-city').text
                item['Price'] = flight_block.find_element(By.CSS_SELECTOR, 'div.price_currency').text
                item['Promotion'] = promotion  
                yield item
                
                yield {
                    'Date': flight_date
                }
                
        else: pass

