# -*- coding: utf-8 -*-
import scrapy
from hotel_sentiment.items import TripAdvisorScoreItem
# from scrapy_splash import SplashRequest # If you use scrapy_plash, you nedd this code.
import time
import math
import datetime

#TODO use loaders
#to run this use scrapy crawl tripadvisor_more -a start_url='http://some_url'
#for example, scrapy crawl tripadvisor_more -a start_url='https://www.tripadvisor.com/Hotels-g186338-London_England-Hotels.html' -o tripadvisor_london.csv
class TripadvisorScoreSpider(scrapy.Spider):
    name = 'tripadvisor_score'
    
    start_urls = [
        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'
    ]
    

    def __init__(self, *args, **kwargs):
        super(TripadvisorScoreSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
    
    """
    # If you use scrapy_splash, you nedd this code.

    def start_requests(self):
        yield SplashRequest(self.start_urls[0], self.parse,
        args={'wait': 0.5},
    )
    """
    

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
        item = TripAdvisorScoreItem()
        
        """
        Ex.

        "start_urls" is as bellow;

        # アジア  日本  近畿地方  京都府  京都  京都市 ホテル
        'https://www.tripadvisor.jp/Hotels-g298564-Kyoto_Kyoto_Prefecture_Kinki-Hotels.html'

        Kyoto has so many good sightseeing spots, hotels, I promise.
        If you have the little time, you should go there!

        Hotel Name : 祇園畑中
        Hotel URL : 'https://www.tripadvisor.jp/Hotel_Review-g298564-d1071044-Reviews-Gion_Hatanaka-Kyoto_Kyoto_Prefecture_Kinki.html'
        Hotel Address : 上京区新町通中立売仕丁町330番地(御所西)
        Category Name : 京都市のホテル/旅館 (「京都市のホテル/旅館421軒中」から
        Category Population : 421 (「京都市のホテル/旅館421軒中」から「京都市のホテル/旅館」と「軒中」を削除)
        Category Ranking : 36 (「36位」から「位」を削除)
        Rate of Category Ranking : Category Ranking / Category Population (カテゴリーランキングの上位何%？)
        Review Stars : 4.5
        Review Quantity : 969 (but, I can't modify the code so that I'm glad if you change it.)
        Review Qutantity written by Ja, En, Ch :
        % of Review Qutantity written by Ja, En, Ch :
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
            ctg_name = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/a/text()').extract()[0]
            item['ctg_name'] = ctg_name.rstrip('軒中')
        except:
            pass
        
        # Category Population
        try:
            ctg_pplt = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/a/text()').extract()[0]
            item['ctg_pplt'] = ctg_pplt.lstrip('京都市のホテル/旅館').rstrip('軒中')
        except:
            pass
        
        # Category Ranking
        try:
            ctg_rank = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/b/text()').extract()[0]
            item['ctg_rank'] = ctg_rank.rstrip('位')
        except:
            pass
        
        # Rate of Category Ranking
        try:
            ctg_pplt = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/a/text()').extract()[0]
            ctg_pplt_num = ctg_pplt.lstrip('京都市のホテル/旅館').rstrip('軒中')
            ctg_rank = response.xpath('//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/b/text()').extract()[0]
            ctg_rank_num = ctg_rank.rstrip('位')
            item['rate_ctg_rank']  = int(ctg_rank_num) / int(ctg_pplt_num) 
        except:
            pass

        # Review Stars
        try:
            item['review_stars'] = response.xpath('//div[@class="ui_columns is-multiline reviewsAndDetails"]/div[1]/div[1]/span/text()').extract()[0]
        except:
            pass
        
        # Review Quantity
        try:
            qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            item['review_qty'] = qty.lstrip('(').rstrip(')')
        except:
            pass
        
        # Review Qutantity written by Japanese
        try:
            qty_ja = response.xpath('//label[@for="filters_detail_language_filterLang_ja" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['review_qty_ja'] = qty_ja.lstrip('(').rstrip(')')
        except:
            pass
        
        
        # % of Review Qutantity written by Japanese ※%変換
        try:
            qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            qty_num = qty.lstrip('(').rstrip(')')
            qty_ja = response.xpath('//label[@for="filters_detail_language_filterLang_ja" and @class="label"]/span[@class="count"]/text()').extract()[0]
            qty_ja_num = qty_ja.lstrip('(').rstrip(')')
            item['rate_of_ja']  = int(qty_ja_num) / int(qty_num) 
        except ZeroDivisionError:
            print('ZeroDivisionError')
        except:
            pass

        # Review Qutantity written by English
        try:
            qty_en = response.xpath('//label[@for="filters_detail_language_filterLang_en" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['review_qty_en'] = qty_en.lstrip('(').rstrip(')')
        except:
            pass
        
        
        # % of Review Qutantity written by English
        try:
            qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            qty_num = qty.lstrip('(').rstrip(')')
            qty_en = response.xpath('//label[@for="filters_detail_language_filterLang_en" and @class="label"]/span[@class="count"]/text()').extract()[0]
            qty_en_num = qty_en.lstrip('(').rstrip(')')
            item['rate_of_en']  = int(qty_en_num) / int(qty_num)
        except ZeroDivisionError:
            print('ZeroDivisionError')
        except:
            pass
        
        # Review Qutantity written by 中国語 (簡) 
        try:
            qty_zhCN = response.xpath('//label[@for="filters_detail_language_filterLang_zhCN" and @class="label"]/span[@class="count"]/text()').extract()[0]
            item['review_qty_zhCN'] = qty_zhCN.lstrip('(').rstrip(')')
        except:
            pass
        
        # % of Review Qutantity written by 中国語 (簡) 
        try:
            qty = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
            qty_num = qty.lstrip('(').rstrip(')')
            qty_zhCN = response.xpath('//label[@for="filters_detail_language_filterLang_zhCN" and @class="label"]/span[@class="count"]/text()').extract()[0]
            qty_zhCN_num = qty_zhCN_num.lstrip('(').rstrip(')')
            item['rate_of_zhCN'] = int(qty_zhCN_num ) / int(qty_num)
        except ZeroDivisionError:
            print('ZeroDivisionError')
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
