# for Chrome driver
from shutil import which

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS = []

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}

BOT_NAME = "firmware"

SPIDER_MODULES = ["firmware.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

DOWNLOAD_HANDLERS = {
    's3': None,
}

ITEM_PIPELINES = {
    "firmware.pipelines.FirmwarePipeline": 1,
}

FILES_STORE = "./output/"

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0
AUTOTHROTTLE_MAX_DELAY = 15
CONCURRENT_REQUESTS = 8

DOWNLOAD_TIMEOUT = 1200
DOWNLOAD_MAXSIZE = 0
DOWNLOAD_WARNSIZE = 0

ROBOTSTXT_OBEY = False
USER_AGENT = "FirmwareBot/1.0 (+https://github.com/firmadyne/scraper)"

#SQL_SERVER = "127.0.0.1"
FACT_INSTANCE = "http://localhost:5000"
