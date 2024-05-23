# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightscraperItem(scrapy.Item):
    # define the fields for your item here like:
    Date = scrapy.Field()
    DepartureTime = scrapy.Field()
    DepartureAirport = scrapy.Field()
    FlightDuration = scrapy.Field()
    FlightNumber = scrapy.Field()
    ArrivalTime = scrapy.Field()
    ArrivalAirport = scrapy.Field()
    Price = scrapy.Field()
    Promotion = scrapy.Field()
    
