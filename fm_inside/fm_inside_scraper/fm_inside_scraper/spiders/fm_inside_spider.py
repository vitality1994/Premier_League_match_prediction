
import scrapy

class fm_inside_spider(scrapy.Spider):
    name = 'fm_inside'


    with open("/Users/jooyong/github_locals/CSCI5525_project/fm_inside/fm_inside_scraper/list_links.txt", "r") as f:
        lines = f.read().splitlines()


    start_urls = lines

    def parse(self, response):
        for attributes in response.css('div.block.stats'):
            yield {
                'name':  response.css('div.column').css('span.value::text').getall()[0],
                'attribute': response.css('div.block.stats').css('div.column').css('td.name').css('acronym::text').getall(),
                'level': attributes.css('tr').css('td::text').getall(),
                'ability': response.css('div.meta').css('span[id="ability"]::text').get(),
                'potential': response.css('div.meta').css('span[id="potential"]::text').get(),
                'club_team': response.css('div.meta').css('span.value::text').get(),
                'nationality': response.css('div.meta').css('span.value').css('a::text').get(),
                'age': response.css('div.column').css('span.value::text').getall()[1],
                'positions': response.css('div.column').css('span.desktop_positions').css('span.position.natural::text').getall(),
                'player_other_info_keys': response.css('div.column').css('span.key::text').getall()[3:11],
                'player_other_info_values': response.css('div.column').css('span.value::text').getall()[2:10],
                'player_main_roles_keys(suitable)': response.css('ol[id="suitable"]').css('span.key::text').getall(),
                'player_main_roles_values(suitable)': response.css('ol[id="suitable"]').css('span.value::text').getall(),
                'player_main_roles_keys(not-suitable)': response.css('ol[id="non-suitable"]').css('span.key::text').getall(),
                'player_main_roles_values(not-suitable)': response.css('ol[id="non-suitable"]').css('span.value::text').getall(),
                'player min_rolesplayeer_minor_roles': response.css('ol[id="suitable"]').css('li.last').css('option::text').getall()
            }
