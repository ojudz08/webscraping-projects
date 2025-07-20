"""
    Author: Ojelle Rogero
    Email: ojelle.rogero@gmail.com
    Created on: March 14, 2021
    Completed on:

    Get news articles and headline using scrapy library from
         Business World: https://www.bworldonline.com/
    Update as of 3/14:
"""

import scrapy

class bwSpider(scrapy.Spider):
    name = "businessworld"

    def start_requests(self):
        urls = [
            'https://www.bworldonline.com/category/top-stories/page/1/',
            'https://www.bworldonline.com/category/top-stories/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        #filename = f'quotes-{page}.html'
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log(f'Saved file {filename}')
        return page

