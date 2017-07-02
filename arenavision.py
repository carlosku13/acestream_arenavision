#Importing modules 
from pattern import web
import requests
from selenium import webdriver
import re
from pattern.web import URL, plaintext
import time
from time import sleep
import os
import sys

#main websites
mains = ['http://arenavision.ru', 'http://arenavision2017.ml', 'http://arenavision2017.tk', 
         'http://arenavision2017.ga', 'http://arenavision2017.cf', 'http://arenavision.in']

#website class
class Website_main(object):
    def __init__(self, main_website):
        self.main_website = main_website
        self.browser_main = webdriver.PhantomJS()
        self.browser_main.set_window_size(1024, 768)
        self.browser_main.get(self.main_website)
        self.website_main = self.browser_main.page_source
        self.browser_main.quit()
        self.dom = web.Element(self.website_main)
        self.links = self.dom.by_class('expanded')
        self.main_url = URL(self.main_website)
    def exists(self):
        if self.main_website.url.exists:
            return True 
        else:
            return False
    def get_links(self):
        url_s = []
        for separator in self.links:
            url_s.extend([self.main_website +  "/" + str(link.href).split('/')[-1] for link in separator('a')[1:]
                 if str(separator('a')[0].href)[1:4] =='ace'])
        channels = {}
        for url in url_s:
            number = re.search(r'\d+', url.split('/')[-1]).group()
            channels[number] = url
        return url_s, channels       
    def schedule_link(self):
        schedule = self.main_website +str(self.dom.by_class('menu')[0]('li')[1]('a')[0].href)
        return schedule

#Schedule class
class Website_schedule(object): 
    def __init__(self, schedule):
        self.schedule = schedule
        self.browser_schedule = webdriver.PhantomJS()
        self.browser_schedule.set_window_size(1024, 768)
        self.browser_schedule.get(self.schedule)
        self.website_schedule = self.browser_schedule.page_source
        self.browser_schedule.quit()
        self.dom_schedule = web.Element(self.website_schedule) 
    def table_exists(self):
        table = self.dom_schedule.by_tag('table')
        if len(table) == 0:
            return False
        else:
            return True
    def get_table(self):
        return self.dom_schedule.by_tag('table')[0]('tr')[1:]

#getting schedule
main = Website_main(mains[0])
for i in range(len(mains)):
    if not main.exists:
        main = Website_main(mains[i+1])
        if not Website_schedule(main.schedule_link()).table_exists():
            main = Website_main(mains[i+1])
        else:
            break
    else:
        if not Website_schedule(main.schedule_link()).table_exists():
            main = Website_main(mains[i+1])
        else:
            break
        break

#function to obtain acestream
def get_acestream(url):
    browser = webdriver.PhantomJS()
    browser.set_window_size(1024, 768)
    browser.get(url)
    website = browser.page_source
    browser.quit()
    dom = web.Element(website)
    aces = dom.by_attr(target = '_blank')
    for ace in aces:
        if ace.href[:3] == 'ace':
            return str(ace.href)

#Function that normalizes the name in table:
def name_column(s):
    return ' '.join(s.encode('utf-8').replace('<br />\n', ' ').replace("&nbsp;", "").split())

#Schedule
schedule = Website_schedule(main.schedule_link())

#Attributes
table = schedule.get_table()
url_s = main.get_links()[0]
channels = main.get_links()[1]

#Obtaining today events and creating dictionary with channels and the different languages:
current_date = time.strftime("%d/%m/%Y")
idx = 0
channels_today = {}
print 'EVENTOS:'
for row in table:
    date = row('td')[0].content
    if date == current_date:
	idx += 1
        time = name_column(row('td')[1].content[:5])
        event = '-'.join([name_column(column.content) for column in row('td')[2:5]])
        channel = name_column(row('td')[5].content).split()
        ch = {}
        for n in range(len(channel)):
            if channel[n][0].isdigit() == False:
                ch[channel[n][1:-1]] = channel[n-1].split('-')
        channels_today[str(idx)] = ch    
        print str(idx)+' // '+time + ' ' + event 
   
#Selecting event, language and channel
current_event =  input('Selecciona evento: ')

language = {}
print 'IDIOMAS:'
for index, item in enumerate(channels_today[str(current_event)].keys()):
    print str(index + 1) + ' // ' + item   
    language[str(index + 1)] = item

current_language = input('Selecciona idioma: ')

channel_to_watch = {}
print 'CANALES:'
for index, item in enumerate(channels_today[str(current_event)][language[str(current_language)]]):
    print str(index + 1) + ' // ' + "Canal " + str(index + 1)
    channel_to_watch[str(index + 1)] = item

current_channel = input('Selecciona canal: ')
print channels[channel_to_watch[str(current_channel)]]

#Getting the acestream link and playing it on Acestream:

acestream = get_acestream(channels[channel_to_watch[str(current_channel)]])

print acestream

