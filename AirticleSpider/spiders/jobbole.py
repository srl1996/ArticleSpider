# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse

from AirticleSpider.items import JobboleAirticleItem,AriticleItemLoader
from AirticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页的url进行下载并交给解析函数进行具体字段的解析
        2.获取下一页的url交给scrapy进行下载,下载完成之后交给parse
        :param response:
        :return:
        """
        #1
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url , post_url),meta= {"front_image_url":image_url}, callback=self.parse_detail)

        #2
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url , post_url), callback=self.parse)


    def parse_detail(self,response):
        # airticle_item = JobboleAirticleItem()
        # front_image_url = response.meta.get("front_image_url" , "")
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(" ·", "").strip()
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # category = response.xpath('//a[@class="category"]/text()').extract()[0]
        # auther = response.xpath('//a[@target="_blank"]/text()').extract()[0]
        #
        # #通过item默认读取
        # airticle_item["url_object_id"] = get_md5(response.url)
        # airticle_item["title"] = title
        # try:
        #     create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # airticle_item["create_date"] = create_date
        # airticle_item["url"] = response.url
        # airticle_item["front_image_url"] = [front_image_url]
        # airticle_item["praise_nums"] = praise_nums
        # airticle_item["fav_nums"] = fav_nums
        # airticle_item["comment_nums"] = comment_nums
        # airticle_item["category"] = category
        # airticle_item["auther"] = auther
        # airticle_item["content"] = content


        #通过Itemloader加载item
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = AriticleItemLoader(item = JobboleAirticleItem(),response = response)
        item_loader.add_xpath("title",'//div[@class="entry-header"]/h1/text()')
        item_loader.add_value("url",response.url)
        item_loader.add_xpath("create_date",'//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_xpath('praise_nums','//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath('fav_nums','//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath('comment_nums','//a[@href="#article-comment"]/span/text()')
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_value('front_image_url',[front_image_url])
        item_loader.add_xpath('content','//div[@class="entry"]')
        item_loader.add_xpath('category','//a[@class="category"]/text()')
        item_loader.add_xpath('auther','//a[@target="_blank"]/text()')

        airticle_item = item_loader.load_item()
        yield airticle_item
