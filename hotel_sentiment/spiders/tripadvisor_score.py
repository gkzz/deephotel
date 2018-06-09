# -*- coding: utf-8 -*-
import scrapy
from hotel_sentiment.items import TripAdvisorScoreItem
import time
import math
import datetime

#TODO use loaders
#to run this use scrapy crawl tripadvisor_more -a start_url='http://some_url'
#for example, scrapy crawl tripadvisor_more -a start_url='https://www.tripadvisor.com/Hotels-g186338-London_England-Hotels.html' -o tripadvisor_london.csv
class TripadvisorScoreSpider(scrapy.Spider):
    name = 'tripadvisor_score'
    
    """
    start_urls = [
        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'
    ]
    
    """

    def __init__(self, *args, **kwargs):
        super(TripadvisorScoreSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
    

    def parse(self, response):
        for href in response.xpath('//a[@class="property_title prominent"]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_score)

        # next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/child::*[2][self::a]/@href')
        next_page = response.xpath('//div[@class="pageNumbers"]/a/@href')   

        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)
       
    def parse_score(self, response):
        item = TripAdvisorStarItem()
        
        """
        Ex.

        "start_urls" is as bellow;

        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'

        Kyoto has so many good sightseeing spots, hotels, I promise.
        If you have the little time, you should go there!

        Hotel Name : ホテル京阪 ユニバーサル・タワー
        Hotel URL : 'https://www.booking.com/hotel/jp/hotel-keihan-universal-tower.ja.html'
        Hotel Address : 上京区新町通中立売仕丁町330番地(御所西)
        Category Name : 京都市のホテル/旅館421軒中
        Category Ranking : 36位
        Review Stars : 4.5
        Review Quantity : 969 (but, I can't modify the code so that I'm glad if you change it.)
        Review Qutantity written by Japanese  : 
        Datetime : Date & Time Logged by This Python File
        Date : Only Date

        """

        # Hotel Name
        try:
            item['hotel_name'] = response.xpath('//h1[@class="ui_header h1"]/text()').extract()[0]
        except:
            # Not all reviews have a logged in reviewer
            pass
        
        # Hotel URL
        try:
            item['hotel_url'] = response.url
        except:
            pass

        # Hotel Address
        try:
            item['hotel_address'] = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[2]/div/div/div/div/span[2]/span[2]/text()').extract()[0]
        except:
            pass

        # Category Name
        try:
            item['ctg_name'] = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/a/text()').extract()[0]
        except:
            pass
        
        # Category Ranking
        try:
            item['ctg_ranking'] = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/b/text()').extract()[0]
        except:
            pass
        
        # Review Stars
        try:
            item['review_stars'] = response.xpath('//div[@class="ui_columns is-multiline reviewsAndDetails"]/div[1]/div[1]/span/text()').extract()[0]
        except:
            pass
        
        # Review Quantity
        try:
            # item['review_qty '] = response.xpath('//div[@class="ui_columns is-multiline reviewsAndDetails"]/div[1]/div[1]/a[2]/text()').extract()[0]
            item['review_qty'] = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
        except:
            pass
        
        # Review Qutantity written by Japanese
        try:
            # item['review_qty '] = response.xpath('//div[@class="ui_columns is-multiline reviewsAndDetails"]/div[1]/div[1]/a[2]/text()').extract()[0]
            item['review_qty_ja'] = response.xpath('//label[@for="filters_detail_language_filterLang_ja" and @class="label"]/span[@class="count"]/text()').extract()[0]
        except:
            pass

        # % of Review Qutantity written by Japanese
        try:
            review_qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            review_qty_ja = response.xpath('//label[@for="filters_detail_language_filterLang_ja" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['rate_of_ja'] = int(review_qty_ja ) // int(review_qty)
        except:
            pass
        
        # Review Qutantity written by English
        try:
            item['review_qty_en'] = response.xpath('//label[@for="filters_detail_language_filterLang_en" and @class="label"]/span[@class="count"]/text()').extract()[0]
        except:
            pass

        # % of Review Qutantity written by English
        try:
            review_qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            review_qty_en = response.xpath('//label[@for="filters_detail_language_filterLang_en" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['rate_of_en'] = int(review_qty_en ) // int(review_qty)
        except:
            pass
        
        # Review Qutantity written by 中国語 (簡) 
        try:
            item['review_qty_zhCN'] = response.xpath('//label[@for="filters_detail_language_filterLang_zhCN" and @class="label"]/span[@class="count"]/text()').extract()[0]
        except:
            pass

        # % of Review Qutantity written by 中国語 (簡) 
        try:
            review_qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            review_qty_zhCN = response.xpath('//label[@for="filters_detail_language_filterLang_zhCN" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['rate_of_zhCN'] = int(review_qty_zhCN ) // int(review_qty)
        except:
            pass
        
        # Hotel Lowest Price
        # item['tr_lowest'] = response.xpath('//div[@class="no_cpu offer premium chevron first hacComplete  avail  lowestPriceFlagPresent"]//div/div[1]/span/img/text()').extract()[0]
        
        # Datetime
        try:
            item['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # Date
        try:
            item['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        except:
            pass

        return item