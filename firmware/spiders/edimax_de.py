import scrapy.http
from scrapy import Spider
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from scrapy.http import HtmlResponse
from selenium.webdriver.support.wait import WebDriverWait
import logging
import urllib.parse
import re
from dateutil.parser import parse

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

logger = logging.getLogger(__name__)

class EdimaxDESpider(Spider):
    name = "edimax_de"
    vendor = "Edimax"

    start_urls = ["https://www.edimax.com/edimax/download/download/data/edimax/de/download/"]

    def start_requests(self):
        url = "https://www.edimax.com/edimax/download/download/data/edimax/de/download/"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time = 5)
    def parse(self, response):
        driver = response.request.meta['driver']
        # Find the select element by its class name
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'step1_select_cb')))
        solution_box = driver.find_element(By.CLASS_NAME, 'step1_select_cb')
        solution_select = Select(driver.find_element(By.CLASS_NAME, 'step1_select_cb'))
        # Get all option elements within the select element
        option_elements = solution_box.find_elements(By.TAG_NAME, ('option'))
        # Extract the value attribute from each option element
        options = [option_element.get_attribute('value') for option_element in option_elements]
        for option in options:
            if option != '':
                solution_select.select_by_value(option)
                sleep(1)
                # find the category box and select an option
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'step2_select_cb')))
                category_box = Select(driver.find_element(By.CLASS_NAME, 'step2_select_cb'))
                category_element = driver.find_element(By.CLASS_NAME, 'step2_select_cb')
                # Get all option elements within the category element
                option_elements = category_element.find_elements(By.TAG_NAME, ('option'))
                # Extract the value attribute from each option element
                options = [(option_element.get_attribute('text'), option_element.get_attribute('value'))  for option_element in option_elements]
                # loop through option
                for option_text, option_value in options:
                    category = option_text
                    if option_value != "":
                        category_box.select_by_value(option_value)
                        sleep(1)
                        # find the modelNo box and select an option
                        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'step3_select_cb')))
                        modelNo_box = Select(driver.find_element(By.CLASS_NAME, 'step3_select_cb'))
                        modelNo_element = driver.find_element(By.CLASS_NAME, 'step3_select_cb')
                        # Get all option elements within the modelNo element
                        option_elements = modelNo_element.find_elements(By.TAG_NAME, ('option'))
                        # Extract the value attribute from each option element
                        options = [option_element.get_attribute('value') for option_element in option_elements]
                        # loop through options
                        for option in options:
                            if option != '':
                                modelNo_box.select_by_value(option)
                                sleep(5)
                                response = HtmlResponse(url=driver.current_url, body=driver.page_source, encoding='utf-8')
                                item = self.parse_product(response,category)
                                if item is not None:
                                    yield item.load_item()
    def parse_product(self, response, category):
        category = category
        base_url = "https://www.edimax.com"
        canvas = response.css("#side2 > div.canvas_post")
        firmware_div = canvas.css("#d_firmware").getall()
        if firmware_div:
            try:
                firmware_table = canvas.css("div:nth-child(19) > table")
                print(firmware_table.getall())
                table_rows = firmware_table.css("tbody > tr")
                for table_row in table_rows:
                    item = FirmwareLoader(
                        item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                    item.add_value("vendor", self.vendor)
                    fw_link = table_row.css("td:nth-child(4) > a::attr('href')").get()
                    fw_link = urllib.parse.urljoin(base_url, fw_link)
                    title_td = table_row.css("td:nth-child(1)")
                    spans = title_td.css("span")
                    for span in spans:
                        span_text = span.css("::text").get()
                        try:
                                date = parse(span_text, fuzzy=True).date().strftime("%Y-%m-%d")
                                print("Extracted date:", date)
                        except ValueError:
                            print("No valid date found.")
                            date = "1970-01-01"
                    item.add_value('url', fw_link)
                    item.add_value('date', date)
                    item.add_value('language', "English")
                    item.add_value('size', "size")
                    item.add_value("description", "")
                    product = canvas.css("div.view_pd_box > a > div > h3::text").get()
                    item.add_value("product", product)
                    item.add_value("category", category)
                    version = title_td.css("::text").getall()
                    version = ''.join(version)
                    # Extract the version using the patterns
                    version_pattern1 = r"\(Version\s*:\s*([\d\.]+)\)" #for (Version : 2.6.3) pattern in Version span
                    version_pattern2 = r"\(Version\s*:\s*v([\d\.]+)\)" #for (Version : v1.29) pattern in Version Span
                    version_pattern3 = r"\(Version\s*:\s*v([\d\.]+[a-zA-Z]?)\)"  # for (Version : v2.49a) pattern in Version Span
                    match = re.search(version_pattern1, version) or re.search(version_pattern2, version or re.search(version_pattern3))
                    if match is not None:
                        version = match.group(1)
                    else:
                        version = "undef"
                    item.add_value("version", version)
                    return item
            except Exception as e:
                print(e)
        else:
            return None

