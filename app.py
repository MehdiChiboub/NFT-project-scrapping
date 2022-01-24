import time
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from selenium.common.exceptions import NoSuchElementException

app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "http://127.0.0.1:4200/"}})
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# selenium options
option = webdriver.ChromeOptions()
option.add_argument("--start-maximized")
option.add_argument("--incognito")
option.add_argument('--ignore-certificate-errors')

# MongoDb options
cluster = MongoClient("mongodb+srv://bilalkh:testtest123@cluster0.kdcdr.mongodb.net/myFirstDatabaseretryWrites=true&w=majority")
db = cluster["nft"]
collection1 = db["recent-collections"]
collection2 = db["top-collections"]
collection = db["all-collections"]
recentData = []
topData = []
dbData = []
dbDataElement = {}

@app.route('/recent-collections' , methods = ['GET'])
def recent_collections():
    browser = webdriver.Chrome(executable_path='C:\\Users\\Probook\\Desktop\\Master SIM\\S3\\JEE\\Projet\\chromedriver_win32\\chromedriver', options=option)
    url = 'https://rarity.tools'
    browser.get(url)
    time.sleep(10)
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

    # insert into MongoDB
    collection1.insert_many(recentData)

@app.route('/top-collections' , methods = ['GET'])
def top_collections():
    browser = webdriver.Chrome(executable_path='C:\\Users\\Probook\\Desktop\\Master SIM\\S3\\JEE\\Projet\\chromedriver_win32\\chromedriver', options=option)
    url = 'https://rarity.tools'
    browser.get(url)
    time.sleep(10)
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
    collection2.insert_many(topData)

@app.route('/all-collections' , methods = ['GET'])
def all_collections():
    browser = webdriver.Chrome(executable_path='C:\\Users\\Probook\\Desktop\\Master SIM\\S3\\JEE\\Projet\\chromedriver_win32\\chromedriver', options=option)
    url = 'https://rarity.tools'
    browser.get(url)
    time.sleep(10)
    # All Collections
    recent_data = browser.find_elements(by=By.CLASS_NAME, value='tableHolder')[1]
    for i in recent_data.find_elements_by_tag_name("tr"):
        if index == 0:
            index = index + 1
            continue
            # print(i.text)

        onLine = []
        attributes = ["number", "name", "volume(7d)", "Sales(7d)", "volume(all time)", "sales all time", "avg price(7d)", "totalSupply", "owners", "owners%", "estimatedMarketCap", "Added"]
        num = 0
        for line in i.text.splitlines():
            if num == 2:
                for info in line.split(" "):
                    if info == "ETH":
                        continue
                    onLine.append(info)
                continue
            onLine.append(line)
            num = num + 1
            
        dbDataElement = {}
        for myIndex in range(len(attributes)):
            dbDataElement[attributes[myIndex]] = onLine[myIndex]

        dbDataElement["link"] = i.find_element_by_tag_name("a").get_attribute('href')
        dbDataElement["image"] = i.find_element_by_tag_name("img").get_attribute('src')
        print(dbDataElement)
        dbData.append(dbDataElement)
            
    for i in range(len(dbData)):
        print(dbData[i])
        url = dbData[i]["link"]
        browser.get(url)
        time.sleep(10)
        socialData = browser.find_elements_by_xpath("//div[contains(@class, 'flex flex-row items-center space-x-1 text-sm')]")
        imgCover = browser.find_elements_by_xpath("//div[contains(@class, 'w-full mb-5 overflow-hidden')]")
        description = browser.find_elements_by_xpath("//div[contains(@class, 'text-sm text-gray-400 notes')]")
        nftsElements = browser.find_elements_by_xpath("//div[contains(@class, 'flex flex-row flex-wrap justify-start px-1 py-2 pt-1 ml-4 lg:px-2')]")
            
        try:
            print("IMAGE")
            print(imgCover[0].find_element_by_tag_name("img").get_attribute('src'))
            dbData[i]["imgCover"] = imgCover[0].find_element_by_tag_name("img").get_attribute('src')

            print("DESCRIPTION")
            dbData[i]["description"] = description[0].text
        except IndexError:
            pass
            
            
        nfts = []
        try:
            print(len(nftsElements[0].find_elements_by_class_name("transition-all")))
            for nft in nftsElements[0].find_elements_by_class_name("transition-all"):
                print(nft.find_element_by_tag_name("img"))
                nfts.append({"img": nft.find_element_by_tag_name("img").get_attribute('src'), "title": nft.find_elements_by_tag_name('a')[2].text})
                print(len(nfts))
        except (NoSuchElementException, IndexError) as error:
            pass
            
        dbData[i]["nfts"] = nfts
            

        for d in socialData:
            print(d.find_element_by_tag_name("a").get_attribute('href'))
            dbData[i][d.find_element_by_tag_name("a").text] = d.find_element_by_tag_name("a").get_attribute('href')

    collection.insert_many(dbData)


if __name__ == '__main__':
   app.run(debug=True)