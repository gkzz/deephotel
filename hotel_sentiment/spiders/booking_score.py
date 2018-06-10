# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from hotel_sentiment.items import BookingScoreItem
# from scrapy_splash import SplashRequest # If you use scrapy_splash, you nedd this code.
import time
import math
import datetime


class BookingScoreSpider(scrapy.Spider):
    name = 'booking_score'
    start_urls = [
        # 大阪市 大人2名 1室 チェックイン日は未指定
        'https://www.booking.com/searchresults.ja.html?city=-240905;ss=%E5%A4%A7%E9%98%AA%E5%B8%82'
        
        """
        Q. How to get the "shorter" (Simple) start_urls??
        A. My way is as bellow;
        1st: scrapy shell 'xxxxxxxxxxxxxxxxxxxxxxxxx' ← too long URL!!
        2nd: >response.url
        'xxxxxx' ← "shorter" URL!!
        So Easy!!! You should try it!!

        """
    ]

    def __init__(self, *args, **kwargs):
        super(BookingScoreSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
    
    """
    # If you use scrapy_splash, you nedd this code.

    def start_requests(self):
        yield SplashRequest(self.start_urls[0], self.parse,
        args={'wait': 0.5},
    )
    """
    
    def start_requests(self):
        yield SplashRequest(self.start_urls[0], self.parse,
        args={'wait': 0.5},
    )
    

    # Get the hotel pages
    def parse(self, response):
        for hotelurl in response.xpath('normalize-space(//a[@class="hotel_name_link url"]/@href)'):
            url = response.urljoin(hotelurl.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//a[starts-with(@class,"paging-next")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)
    
    # Get its review list's pages
    def parse_hotel(self, response):
        try:
            list_url = response.xpath('//a[@class="show_all_reviews_btn"]/@href')
            url = response.urljoin(list_url[0].extract())
            return scrapy.Request(url, callback=self.parse_score_scrape)
        except:
            return scrapy.Request(url, callback=self.parse)

    # Get the items
    def parse_score_scrape(self, response):
        item = BookingScoreItem()

        """
        Ex.

         "start_urls" is as bellow;

        # 大阪市 大人2名 1室 チェックイン日は未指定
        'https://www.booking.com/searchresults.ja.html?city=-240905;ss=%E5%A4%A7%E9%98%AA%E5%B8%82'

        Hotel Name : 大阪マリオット都ホテル
        Hotel URL : 'https://www.booking.com/reviews/jp/hotel/osaka-marriott-miyako.ja.html'
        Hotel Address : 〒545-0052 大阪府, 大阪市, 阿倍野区阿倍野筋1-1-43
        Category Name : 大阪市のホテルランキング
        Category Population: 
        Category Ranking : 1位
        Review Score : 9.4
        Review Quantity : ホテルのクチコミ1935件の評価
        Score of 1st Review Category (Cleanliness 清潔さ) : 9.6
        Score of 2nd Review Category (Comfort 快適さ) : 9.5
        Score of 3rd Review Category (Location ロケーション) : 9.5
        Score of 4th Review Category (Facilities 施設・設備) : 9.5
        Score of 5th Review Category (Staff スタッフ) : 9.5
        Score of 6th Review Category (Value for money お得感) : 8.6
        Score of 7th Review Category (Free WiFi WiFi(無料)) : 9.4
        Datetime : Date & Time Logged by This Python File
        Date : Only Date
        """

        # Hotel Name
        try:
            item['hotel_name']  = response.xpath('normalize-space(//h1[@class="item hotel_name"]/a/text())').extract()[0]
        except:
            pass
        
        # Hotel URL
        try:
            item['hotel_url'] = response.url
        except:
            pass

        # Hotel Address
        try:
            item['hotel_address'] = response.xpath('normalize-space(//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/p/text())').extract()[0]
        except:
            pass
        
        # Category Name 
        try:
            item['ctg_name'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/a/text()').extract()[0]
        except:
            pass
        
        # Category Population　※
        try:
            item['ctg_pplt'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/text()[2]').extract()[0]
        except:
            pass

        # Category Ranking
        try:
            rank = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/strong/text()').extract()[0]
            item['ctg_rank'] = rank.rstrip('位')
        except:
            pass
                
        # Review Score
        try:
            item['review_score'] = response.xpath('normalize-space(//span[contains(@class, "review-score-widget")]/span[@class="review-score-badge"]/text())').extract()[0]
        except:
            pass
        
        # Review Quantity
        try:
            qty = response.xpath('normalize-space(//div[@class="review_list_score_container lang_ltr "]/p[@class="review_list_score_count"]/text())').extract()[0]
            item['review_qty'] = qty.lstrip('ホテルのクチコミ').rstrip('件の評価')
        except:
            pass
        
        # Cleanliness
        try:
            item['clean'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[1]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Comfort
        try:
            item['comf'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[2]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Location
        try:
            item['loct'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[3]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Facilities
        try:
            item['fclt'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[4]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Staff
        try:
            item['staff'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[5]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Value for Money
        try:
            item['vfm'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[6]/p[2]/text())').extract()[0]
        except:
            pass
        
        # Free WiFi
        try:
            item['wifi'] = response.xpath('normalize-space(//*[@id="review_list_score_breakdown"]/li[7]/p[2]/text())').extract()[0]
        except:
            pass

        # Datetime
        try:
            item['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # Date
        try:
            item['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        except:

        yield item

        next_page = response.xpath('//a[@id="review_next_page_link"]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_reviews)
