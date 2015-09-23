import scrapy
import time

url = "https://www.zomato.com/ncr/restaurants?page=%d"
class ZomatoSpider(scrapy.Spider):
    name = 'zomato'
    start_urls = [url % 1]

    def parse(self, response):
        self.page_no = 1
        while self.page_no<2:
            for href in response.css('.search-result-all h3 a::attr(href)'):
                full_url = response.urljoin(href.extract())
                yield scrapy.Request(full_url, callback=self.parse_restaurant)
            yield scrapy.Request(url % self.page_no)
            self.page_no +=1
            #if "Bandwidth exceeded" in response.body:
                #raise CloseSpider("bandwidth_exceeded")

    def parse_restaurant(self, response):
        location = self.extractLocation(response)
        rate = self.rate(response)
        votes = self.votes(response)
        costs = self.costs(response)
        timming = self.timming(response)

        yield {
            'link' : response.url,
            'name': response.css('.res-name a span::text').extract()[0].strip(),
            'location': location,
            'rating': rate,
            'votes': votes,
            'cost': costs, 
            'timing': timming
        }

    def extractLocation(self, response):
        location = response.css('.resmap-img::attr(style)').extract()[0].strip()
        list1 = []
        address = response.css(".res-main-address .res-main-address-text::text").extract()[0].strip()
        list1.append(address[:])
        ad = response.css(".res-main-address .res-main-address-text span::text").extract()[0].strip()
        list1.append(ad[:])
        if len(address)>0 and location:
            location = location.split('|')[2].split(',')
            return { "address": list1[0], "locality": list1[1], "latitude": float(location[0]), "longitude": float(location[1])}
        else:
            return "Null"
        
    def rate(self, response):
        rate = response.css('.rating-info .res-rating div::text').extract()[0].strip()
        return float(rate)
    def votes(self, response):
        votes = response.css(".rating-info .rating-votes-div span span::text").extract()[0].strip()
        if len(votes)>0:
            return int(votes[:])
        else:
            return "null"
    def costs(self, response):
        costs = response.css(".res-imagery-body.zhl3-bg.is-responsive.en .res-imagery-default.imagery.item-to-hide-parent #mainframe.wrapper.container.plr0i .col-l-12.res-left-area .row div.col-m-5.resinfo.divider--right.pr0 .resbox__main--row .res-info-group.clearfix .res-info-detail span::text").extract()
        rupee = "Rs."
        com = ","
        if len(costs)>0:
            for cost in costs:
                if rupee in cost:
                    cost=(cost.split()[1])
                    if com in cost:
                        cost = cost.split(",")
                        return int(cost[0] + cost[1])
                    else:
                        return int(cost)
        else:
            return "Null"
    
        
    def func(lis):
        if len(lis)>0:
            return lis
        else:
            return "null"
    def timming(self, response):
        timming = response.css(".res-imagery-body.zhl3-bg.is-responsive.en .res-imagery-default.imagery.item-to-hide-parent #mainframe.wrapper.container.plr0i .col-l-12.res-left-area .row div.col-m-5.resinfo.divider--right.pr0 .resbox__main--row .res-info-group.clearfix .res-info-detail span::text").extract()[2].split()
        
        if len(timming)>0:
            opening = checktime(timming[:2])
            closing = checktime(timming[3:])
            return {"opening": opening, "closing": closing}
        else:
            return "null"

def checktime(lst):
    for i in range(len(lst)):
        if lst[i] =="AM":
            return lst[i-1]
        if lst[i] =="PM":
            if ":" in lst[i-1]:
                n = lst[i-1].split(":")
                if n[0] == "12":
                    b = n[0]
                else:
                    b = int(n[0]) + 12
                c= str(b) + ":"+ n[1]
            else:
                b= int(lst[i-1]) + 12
                c = str(b) + ":" + "00"

            return c
        if lst[i] == "Noon":
            return lst[i-1]
        if lst[i] == "Midnight":
            return "00"
if __name__=="__main__":
    ZomatoSpider()
        


