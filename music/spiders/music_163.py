# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request, FormRequest

from music.items import MusicItem
from music.settings import DEFAULT_REQUEST_HEADERS


class Music163Spider(scrapy.Spider):
    name = "music_163"
    allowed_domains = ["music.163.com"]
    start_urls = ['http://music.163.com']
    initials = [str(i) for i in range(65,91)]

    def start_requests(self):
        # for initial in self.initials:
        url = '{url}/discover/artist/cat?id=1001&initial={initial}'.format(url=self.start_urls[0], initial='65')
        yield Request(url, callback=self.parse_index)

    # def parse_index(self, response):
    #     names1 = response.xpath('//*[@id="m-artist-box"]/li/p/a[1]/text()').extract()
    #     names2 = response.xpath('//*[@id="m-artist-box"]/li/a[1]/text()').extract()
    #     namess = names1 + names2
    #     for name in namess:
    #         item = MusicItem()
    #         item['name'] = name
    #         yield item

    def parse_index(self, response):
        artists = response.xpath('//*[@id="m-artist-box"]/li/p/a[1]/@href').extract()
        for artist in artists:
            # item = MusicItem()
            artist_url = self.start_urls[0] + '/artist' + '/album' + artist[8:]
            yield Request(artist_url, callback=self.parse_artist)

    def parse_artist(self, response):
        albums = response.xpath('//*[@id="m-song-module"]/li/p/a/@href').extract()
        for album in albums:
            # item = MusicItem()
            # item['name'] = album
            album_url = self.start_urls[0] + '/' + album[1:]
            # item['name'] = self.start_urls[0] + '/' + album[1:]
            # print(album_url)
            yield Request(album_url, callback=self.parse_album)

    def parse_album(self, response):
        musics = response.xpath('//ul[@class="f-hide"]/li/a/@href').extract()
        # print(musics)
        for music in musics:
            music_id = music[9:]
            music_url = self.start_urls[0] + music
        #     item['link'] = music_url
            yield Request(music_url, meta={'id': music_id}, callback=self.parse_music)


    def parse_music(self, response):
        music_id = response.meta['id']
        music = response.xpath('//div[@class="tit"]/em[@class="f-ff2"]/text()').extract_first()
        artist = response.xpath('//div[@class="cnt"]/p[1]/span/a/text()').extract_first()
        album = response.xpath('//div[@class="cnt"]/p[2]/a/text()').extract_first()
        # print(music_id, music, artist, album)

        data = {
            'csrf_token': '',
            'params': '2IQJkONJgwsVCSf87vwUWX7cgb0BmFDpqfCZAwUv9HwjexkjlVtQjEQGj767QlEC11Nm6ed8J94HQtz2JhACe20eLiVAA5b9dtBnxCW4SFP/4dswTvMwQk+bZNvKJfqbfmxO1Zcxm9aKHK1q7T214A==',
            'encSecKey': '4283343d28b8a27634e08e2611fe5ba129d52d961e7fb3afc4a29c2a95f0f6c8ff758bac30fc27add103899c7a159d991db037cd7613949217de5357f1d808d4907fa7f1bb87dde148e152f591da45e74c51cf3c5ca9ca8f19320e7267cc1313e3ba120e6995a1b639aaee73c9bd9295977dd3947df636451eaf57d252bdc590'
        }
        DEFAULT_REQUEST_HEADERS['Referer'] = self.start_urls[0] + '/song?id=' + str(music_id)
        music_comment = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(music_id)

        # item = MusicItem()
        # item['name'] = music_id
        # item['link'] = music
        # yield item
        #
        yield FormRequest(music_comment,
                          meta={'id': music_id, 'music': music, 'artist': artist, 'album': album},
                          callback=self.parse_comment, formdata=data)

    def parse_comment(self, response):
        id = response.meta['id']
        music = response.meta['music']
        artist = response.meta['artist']
        album = response.meta['album']
        result = json.loads(response.text)
        comments = []
        if 'hotComments' in result.keys():
            for comment in result.get('hotComments'):
                hotcomment_author = comment['user']['nickname']
                hotcomment = comment['content']
                hotcomment_like = comment['likedCount']
                # 这里我们将评论的作者头像也保存，如果大家喜欢这个项目，我后面可以做个web端的展现
                hotcomment_avatar = comment['user']['avatarUrl']
                data = {
                    'nickname': hotcomment_author,
                    'content': hotcomment,
                    'likedcount': hotcomment_like,
                    'avatarurl': hotcomment_avatar
                }
                comments.append(data)

        item = MusicItem()
        # 由于eval方法不稳定，具体的可以自己搜索，我们过滤一下错误
        # for field in item.fields:
        #     try:
        #         item[field] = eval(field)
        #     except:
        #         print('Field is not defined', field)
        item['id'] = id
        item['artist'] = artist
        item['album'] = album
        item['music'] = music
        item['comments'] = comments
        yield item

# def parse(self, response):
#     for each in response.xpath('//ul[@id="m-pl-container"]/li'):
#         item = MusicItem()
#         item['count'] = each.xpath('./div/div/span[2]/text()').extract()[0]
#         item['namess'] =each.xpath('./p[1]/a/text()').extract()[0]
#         yield item