# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from hotel_sentiment.items import BookingReviewItem
# from scrapy_splash import SplashRequest # If you use scrapy_splash, you nedd this code.
import time
import math
import datetime


class BookingReviewSpider(scrapy.Spider):
    name = 'booking_review'
    
    """
    start_urls = [
        # 大阪市 大人2名 1室 チェックイン日は未指定
        'https://www.booking.com/searchresults.ja.html?city=-240905;ss=%E5%A4%A7%E9%98%AA%E5%B8%82'
    ]
    
    """

    def __init__(self, *args, **kwargs):
        super(BookingReviewSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
    
    """
    # if you use scrapy_splash, you nedd this code.

    def start_requests(self):
        yield SplashRequest(self.start_urls[0], self.parse,
        args={'wait': 0.5},
    )
    """
    

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
            return scrapy.Request(url, callback=self.parse_score)
        except:
            return scrapy.Request(url, callback=self.parse)

    # Go down review pages
    def parse_score(self, response):
        for review_url in response.xpath('//a[@class="review_item_header_content"]/@href'):
            url = response.urljoin(review_url.extract())
            yield scrapy.Request(url, callback=self.parse_review_scrape)

        next_page = response.xpath('//a[@class="page_link review_next_page")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_score)

    # Get the items
    def parse_review_scrape(self, response):
        item = BookingReviewItem()

        """
        Ex.

         "start_urls" is as bellow;

        # 大阪市 大人2名 1室 チェックイン日は未指定
        'https://www.booking.com/searchresults.ja.html?aid=304142&label=gen173nr-1DCAModUIFb3Nha2FIFVgEaHWIAQGYARXCAQp3aW5kb3dzIDEwyAEM2AED6AEB-AECkgIBeagCAw&sid=a3ca5151f3e312bb1d8d56a143859d91&sb=1&src=searchresults&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fsearchresults.ja.html%3Faid%3D304142%3Blabel%3Dgen173nr-1DCAModUIFb3Nha2FIFVgEaHWIAQGYARXCAQp3aW5kb3dzIDEwyAEM2AED6AEB-AECkgIBeagCAw%3Bsid%3Da3ca5151f3e312bb1d8d56a143859d91%3Bcity%3D-240905%3Bclass_interval%3D1%3Bdest_id%3D-240905%3Bdest_type%3Dcity%3Bdtdisc%3D0%3Bfrom_sf%3D1%3Bgroup_adults%3D4%3Bgroup_children%3D0%3Binac%3D0%3Bindex_postcard%3D0%3Blabel_click%3Dundef%3Bno_rooms%3D1%3Boffset%3D0%3Bpostcard%3D0%3Broom1%3DA%252CA%252CA%252CA%3Bsb_price_type%3Dtotal%3Bsrc%3Dsearchresults%3Bsrc_elem%3Dsb%3Bss%3D%25E5%25A4%25A7%25E9%2598%25AA%25E5%25B8%2582%3Bss_all%3D0%3Bssb%3Dempty%3Bsshis%3D0%3Bssne%3D%25E5%25A4%25A7%25E9%2598%25AA%25E5%25B8%2582%3Bssne_untouched%3D%25E5%25A4%25A7%25E9%2598%25AA%25E5%25B8%2582%26%3B&ss=%E5%A4%A7%E9%98%AA%E5%B8%82&ssne=%E5%A4%A7%E9%98%AA%E5%B8%82&ssne_untouched=%E5%A4%A7%E9%98%AA%E5%B8%82&city=-240905&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&from_sf=1'


        Hotel Name : 大阪マリオット都ホテル
        Hotel Address : 大阪市, 阿倍野区阿倍野筋1-1-43
        Review Title : 快適。部屋が綺麗。
        Review URL : 'https://www.booking.com/reviews/jp/hotel/osaka-marriott-miyako/review/20153491a67d3975.ja.html'
        Reviewer Name : 大喜多
        Reviewer Location : 日本
        Reviewer Posting Count : 1件の投稿
        Positive Content : 部屋が広かった。眺めが良かった。朝食。
        Negative Content : お風呂に洗面器がない。
        1st Tag - 5th Tag : 友達 • コネクティング　ダブル＆ツインルーム • 1泊 • xxxx • yyy      
        Staydate : 滞在日：2018年5月
        Datetime : Date & Time Logged by This Python File
        Date : Only Date
        """

        # Hotel Name
        try:
            item['hotel_name']  = response.xpath('normalize-space(//*[@id="b2reviews_reviewPage"]/div[6]/div[1]/div/div[1]/div[1]/text())').extract()[0]
        except:
            pass
            

        # Hotel Address
        try:
            item['hotel_address'] = response.xpath('normalize-space(//p[@class="reviews_review_hotel_address"]/text())').extract()[0]
        except:
            pass
        
        # Review Title
        try:
            item['review_title'] = response.xpath('normalize-space(//h1/span/text())').extract()[0]
        except:
            pass

        # Review URL
        try:
            item['review_url'] = response.url
        except:
            pass

        # Reviewer Name
        try:
            item['reviewer_name'] = response.xpath('normalize-space(//h4/span/text())').extract()[0]
        except:
            pass

        # Reviewer Location
        try:
            item['reviewer_location'] = response.xpath('normalize-space(//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[3]/span/span[2]/span/text())').extract()[0]
        except:
            pass
        
        # Reviewer Posting Count
        try:
            item['posting_conts'] = response.xpath('normalize-space(//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[3]/div[3]/text())').extract()[0]
        except:
            pass

        # Positive Content
        try:
            item['positive_content'] = response.xpath('normalize-space(//p[@class="review_pos "]/span/text())').extract()[0]
        except:
            pass
        
        # Negative Content
        try:
            item['negative_content'] = response.xpath('normalize-space(//p[@class="review_neg "]/span/text())').extract()[0]
        except:
            pass
        
        # 1st Tag ここから
        try:
            item['tag_n1'] = response.xpath('//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[4]/div/ul/li[1]/text()').extract()[1]
        except:
            pass
        
        # 2nd Tag
        try:
            item['tag_n2'] = response.xpath('//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[4]/div/ul/li[2]/text()').extract()[1]
        except:
            pass
        
        # 3rd Tag
        try:
            item['tag_n3'] = response.xpath('//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[4]/div/ul/li[3]/text()').extract()[1]
        except:
            pass
        
        # 4th Tag
        try:
            item['tag_n4'] = response.xpath('//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[4]/div/ul/li[4]/text()').extract()[1]
        except:
            pass
        
        # 5th Tag
        try:
            item['tag_n5'] = response.xpath('normalize-space(//*[@id="b2reviews_reviewPage"]/div[6]/ul/li/div[4]/div/ul/li[5]/text())').extract()[0]
        except:
            pass

        # Staydate
        try:
            item['staydate'] = response.xpath('//p[starts-with(@class, "review_staydate")]/text()').extract()[0]
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
            yield scrapy.Request(url, self.parse_review)
