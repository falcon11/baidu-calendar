 #!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-07-26 10:51:02
# Project: baidu_calendar

from pyspider.libs.base_handler import *

import re
import urllib
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import threading
import json


driver = None
url = 'http://www.baidu.com/s?' + urllib.urlencode({'wd': '日历'})
date_pattern = re.compile(r'date="[\d]+[-][\d]+[-][\d]+"')

def get_calendar(start_year, end_year):
    holiday_list = []
    date_list = []

    driver = webdriver.PhantomJS()
    driver.get(url)

    driver.implicitly_wait(2)

    year_choose_btn = driver.find_element_by_xpath("//div[@class='op-calendar-new-year-box']//div[@class='c-dropdown2-btn-group']")
    month_choose_btn = driver.find_element_by_xpath("//div[@class='op-calendar-new-month-box']//div[@class='c-dropdown2-btn-group']")

    items = driver.find_elements_by_xpath("//ul[@class='c-dropdown2-menubox']")
    years = items[0].find_elements_by_xpath('li')
    monthes = items[1].find_elements_by_xpath('li')

    for year in years:
        if ((int(year.get_attribute('data-value')) >= start_year) and (int(year.get_attribute('data-value')) <= end_year)):
            year_choose_btn.click()
            year.click()
            sleep(1)

            for month in monthes:
                print 'month: ', month.get_attribute('data-value')
                month_choose_btn.click()
                month.click()
                sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                td_div_list = soup.findAll('div',{'class':'op-calendar-new-relative'})
                days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                for td_tag in td_div_list:
                    href_tag = str(td_tag.a)
                    element = td_tag.a
                    if href_tag.find('op-calendar-new-table-other-month') != -1:
                        continue
                    date_str_list = date_pattern.findall(href_tag)
                    if len(date_str_list):
                        date = date_str_list[0].split('"')[1]
                        year, month, day = date.split('-')
                        date = datetime(int(year), int(month), int(day))
                        date_obj = {}
                        date_obj['date'] = '{:%Y%m%d}'.format(date)
                        date_obj['weekday'] = days[date.weekday()].decode('utf-8')
                        date_obj['week'] = date.weekday() + 1
                        if href_tag.find('op-calendar-new-table-weekend') != -1:
                            date_obj['is_weekend'] = True
                        if href_tag.find('op-calendar-new-table-festival') != -1:
                            date_obj['is_festival'] = True
                            festival = element.get('title')
                            if festival == None:
                                festival = element.find('span', class_='op-calendar-new-table-almanac')
                                festival = festival.text
                            print '{:%Y-%m-%d}'.format(date), festival
                            date_obj['festival'] = festival.strip()
                        if href_tag.find('op-calendar-new-table-rest') != -1:
                            date_obj['is_rest'] = True
                        if href_tag.find('op-calendar-new-table-work') != -1:
                            date_obj['is_work'] = True
                        date_list.append(date_obj)
                        if (href_tag.find('op-calendar-new-table-festival') != -1 or href_tag.find('op-calendar-new-table-weekend') != -1):
                            holiday_list.append(date)

    jsonStr = json.dumps(date_list, ensure_ascii=False, indent=4)
    with open('holiday_list.json', 'w') as f:
        f.write(jsonStr.encode('utf-8'))
        print 'saved to holiday_list.json'

    driver.quit()

if __name__ == '__main__':
    try:
        get_calendar(datetime.today().year, datetime.today().year)
    except Exception as e:
        print e
    finally:
        if driver:
            driver.quit()