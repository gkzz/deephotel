# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HotelSentimentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    stars = scrapy.Field()

class TripAdvisorScoreItem(scrapy.Item):
    hotel_name = scrapy.Field()
    hotel_url = scrapy.Field()
    hotel_address = scrapy.Field()
    ctg_name = scrapy.Field()
    ctg_ranking = scrapy.Field()
    review_stars = scrapy.Field()
    review_qty = scrapy.Field()
    review_qty_ja = scrapy.Field()
    rate_of_ja = scrapy.Field()
    review_qty_en = scrapy.Field()
    rate_of_en = scrapy.Field()
    review_qty_zhCN = scrapy.Field()
    rate_of_zhCN = scrapy.Field()
    datetime = scrapy.Field()
    date = scrapy.Field()

class TripAdvisorReviewItem(scrapy.Item):
    hotel_name = scrapy.Field()
    review_title = scrapy.Field()
    review_url = scrapy.Field()
    reviewer_name = scrapy.Field()
    reviewer_location = scrapy.Field()
    content = scrapy.Field()
    tips = scrapy.Field()
    purpose = scrapy.Field()
    datetime = scrapy.Field()
    date = scrapy.Field()

class BookingScoreItem(scrapy.Item):
    hotel_name = scrapy.Field()
    hotel_url = scrapy.Field()
    hotel_address = scrapy.Field()
    ctg_name = scrapy.Field()
    ctg_pplt = scrapy.Field()
    ctg_rank = scrapy.Field()
    review_score = scrapy.Field()
    review_qty = scrapy.Field()
    clean = scrapy.Field()
    comf = scrapy.Field()
    loct = scrapy.Field()
    fclt = scrapy.Field()
    staff = scrapy.Field()
    vfm = scrapy.Field()
    wifi = scrapy.Field()
    datetime = scrapy.Field()
    date = scrapy.Field()

class BookingReviewItem(scrapy.Item):
    hotel_name = scrapy.Field()
    hotel_address = scrapy.Field()
    review_title = scrapy.Field()
    review_url = scrapy.Field()
    reviewer_name = scrapy.Field()
    reviewer_location = scrapy.Field()
    posting_conts = scrapy.Field()
    positive_content = scrapy.Field()
    nesitive_content = scrapy.Field()
    tag_n1 = scrapy.Field()
    tag_n2 = scrapy.Field()
    tag_n3 = scrapy.Field()
    tag_n4 = scrapy.Field()
    tag_n5 = scrapy.Field()
    stardate = scrapy.Field()
    datetime = scrapy.Field()
    date = scrapy.Field()