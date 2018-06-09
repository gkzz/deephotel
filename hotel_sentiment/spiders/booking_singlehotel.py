# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from hotel_sentiment.items import BookingReviewItem


class BookingSpider(scrapy.Spider):
    name = "booking_singlehotel"
    start_urls = [
        #http://www.booking.com/hotel/us/new-york-inn.html,
        #add your url here
        'https://www.booking.com/hotel/us/pennsylvania-new-york.ja.html'
    ]

    #get its reviews page
    def parse(self, response):
        reviewsurl = response.xpath('//a[@class="show_all_reviews_btn"]/@href')
        url = response.urljoin(reviewsurl[0].extract())
        self.pageNumber = 1
        return scrapy.Request(url, callback=self.parse_reviews)

    #and parse the reviews
    def parse_reviews(self, response):
        item = BookingReviewItem()

        """
        Ex.

         "start_urls" is as bellow;

        # ホテル ペンシルバニア（Hotel Pennsylvania）
        'https://www.booking.com/hotel/us/pennsylvania-new-york.ja.html'


        Hotel Name : 祇園畑中
        Hotel Address
        Category Name
        Category Population
        Category Ranking
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
        """
        # Hotel Name
        try:
            item['hotel_name']  = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/h1/a/text()').extract()[0]
        except:
            pass

        # Hotel Address
        try:
            item['hotel_address'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/p/text()').extract()[0]
        except:
            pass
        
        # Category Name
        try:
            item['ctg_name'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/a/text()').extract()[0]
        except:
            pass
        
        """
        # Category Population
        try:
            item['ctg_pplt'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/text()[2]').extract()[0]
        except:
            pass
        """

        # Category Ranking
        try:
            item['ctg_ranking'] = response.xpath('//*[@id="standalone_reviews_hotel_info_wrapper"]/div[1]/div/div/div/p/strong/text()').extract()[0]
        except:
            pass
        
        # Review Title
        try:
            item['review_title'] = 
        except:
            pass

        # Review URL
        try:
            item['review_url'] = response.url
        except:
            pass

        # Reviewer Name
        try:
            item['rev_name'] = 
        except:
            pass

        # Reviewer Location
        try:
            item['reviewer_location'] = response.xpath('//div[@class="userLoc"]/strong/text()').extract()[0]
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
        
         # Positive Content
        try:
            item['positive_content'] = response.xpath('//div[@class="ui_columns is-multiline reviewsAndDetails"]/div[1]/div[1]/span/text()').extract()[0]
        except:
            pass
        
        # Negative Content
        try:
            item['nesitive_content'] = response.xpath('//div[@class="block_header block_title"]/div[1]/span/text()').extract()[0]
        except:
            pass
        
        # Tags
        try:
            item['tag'] = 
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
        
        """