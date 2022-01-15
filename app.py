import time
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymongo import MongoClient

app = Flask(__name__)

# selenium options
option = webdriver.ChromeOptions()
option.add_argument("--start-maximized")
option.add_argument("--incognito")
option.add_argument('--ignore-certificate-errors')

browser = webdriver.Chrome(executable_path='C:\\Users\\Probook\\Desktop\\Master SIM\\S3\\JEE\\Projet\\chromedriver_win32\\chromedriver', options=option)
url = 'https://rarity.tools'
browser.get(url)
time.sleep(10)

# MongoDb options
cluster = MongoClient("mongodb+srv://bilalkh:testtest123@cluster0.kdcdr.mongodb.net/myFirstDatabaseretryWrites=true&w=majority")
db = cluster["nft"]
collection1 = db["recent-collections"]
collection2 = db["top-collections"]
recentData = []
topData = []

# More Recent Collections
recent_data = browser.find_elements(by=By.CLASS_NAME, value='tableHolder')[0]
for ele in recent_data.find_elements_by_tag_name('a'):
    href = ele.get_attribute('href')
    img = ele.find_element_by_tag_name('img').get_attribute('src')
    name = ele.find_element_by_tag_name('div').text
    dict = {
        "name": name,
        "link": href,
        "image": img,
    }
    recentData.append(dict)


# Top Collections
top_data = browser.find_elements_by_xpath("//div[contains(@class, 'pt-4 pb-3 mt-4 border border-gray-300 rounded-lg shadow-md dark:border-gray-800 bgCard ml-4')]")
for ele in top_data:
    div = ele.find_elements_by_tag_name('div')
    for e in div:
        a = e.find_elements_by_tag_name('a')
        for el in a:
            href = el.get_attribute('href')
            img = el.find_element_by_tag_name('img').get_attribute('src')
            name = el.find_element_by_class_name('text-base').text
            volume = el.find_element_by_class_name('text-sm').text
            dict = {
                "name": name,
                "volume": volume,
                "link": href,
                "image": img,
            }
            topData.append(dict)

# insert into MongoDB
collection1.insert_many(recentData)
collection2.insert_many(topData)
