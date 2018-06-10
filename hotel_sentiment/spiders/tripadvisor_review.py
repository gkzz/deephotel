# -*- coding: utf-8 -*-
import scrapy
from hotel_sentiment.items import TripAdvisorReviewItem
# from scrapy_splash import SplashRequest # If you uses scrapy-splash, you nedd this code.
import time
import math
import datetime

#TODO use loaders
#to run this use scrapy crawl tripadvisor_more -a start_url='http://some_url'
#for example, scrapy crawl tripadvisor_more -a start_url='https://www.tripadvisor.com/Hotels-g186338-London_England-Hotels.html' -o tripadvisor_london.csv
class TripadvisorReviewSpider(scrapy.Spider):
    name = 'tripadvisor_review'
    
    """
    start_urls = [
        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'
    ]

    """

    
    """
    # If you uses scrapy-splash, you nedd this code.

    def start_requests(self):
        yield SplashRequest(self.start_urls[0], self.parse,
        args={'wait': 0.5},
    )
    """

    def parse(self, response):
        for href in response.xpath('//a[@class="property_title prominent"]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)
            # yield scrapy.Request(url, callback=self.parse_summary)

        # next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/child::*[2][self::a]/@href')
        next_page = response.xpath('//div[@class="pageNumbers"]/a/@href')   

        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    def parse_hotel(self, response):
        for href in response.xpath('//div[starts-with(@class,"quote")]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_review)

        next_page = response.xpath('//div[@class="unified pagination "]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_hotel)


    #to get the full review content I open its page, because I don't get the full content on the main page
    #there's probably a better way to do it, requires investigation
    def parse_review(self, response):
        item = TripAdvisorReviewItem()

        """
        Ex.

         "start_urls" is as bellow;

        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'

        Kyoto has so many good sightseeing spots, hotels, I promise.
        If you have the little time, you should go there!

        Hotel Name : 祇園畑中
        Review Title
        Review URL : 'https://www.tripadvisor.jp/ShowUserReviews-g298564-d1071044-r577749431-Gion_Hatanaka-Kyoto_Kyoto_Prefecture_Kinki.html'
        Reviewer Name : leo868
        Reviewer Location : 大分市, 大分県
        Content : 立地がよく、混雑をさけ早朝、夜の東山観光に便利。料理は美味しく量も十分。部屋に風呂もあるが大(以下、略)
        Tips : 離れのスタンダード客室で眺望はないが静かでくつろげたが、空室があれば眺望の(以下、略)
        Purpose : 2018年5月、家族旅行
        Datetime : Date & Time Logged by This Python File
        Date : Only Date
        """

        
        # Hotel Name
        try:
            item['hotel_name'] = response.xpath('//*[@id="CHECK_RATES_CONT"]/div/div[1]/div/span/text()').extract()[0]
        except:
            pass
        
        # Review Title
        try:
            item['review_title'] = response.xpath('//h1[@id="HEADING"]/text()').extract()[0]
        except:
            pass

        # Review URL
        try:
            item['review_url'] = response.url
        except:
            pass
        
        # Reviewer Name
        try:
            item['reviewer_name'] = response.xpath('//div[@class="memberOverlayLink"]/div[2]/div[1]/text()').extract()[0]
        except:
            pass
        
        # Reviewer Location
        try:
            item['reviewer_location'] = response.xpath('//div[@class="userLoc"]/strong/text()').extract()[0]
        except:
            pass
        
        # Content
        try:
            # item['content'] = '\n'.join([line.strip() for line in response.xpath('//div[@class="rev_wrap ui_columns is-multiline"]/div[2]/div[3]/div/p/span/text()')[0].extract()])
            item['content'] = response.xpath('//div[@class="rev_wrap ui_columns is-multiline"]/div[2]/div[3]/div/p/span/text()')[0].extract()
        except:
            pass

        # Tips
        try:
            # item['tips'] = '\n'.join([line.strip() for line in response.xpath('//div[@class="reviewItem inlineRoomTip"]/text()')[0].extract()])
            item['tips'] = response.xpath('//div[@class="reviewItem inlineRoomTip"]/text()')[0].extract()
        except:
            pass

        # Purpose
        try:
            item['purpose'] = response.xpath('//div[@class="recommend-titleInline noRatings"]/text()').extract()[0]
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
            pass

        return item
