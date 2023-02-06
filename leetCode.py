from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from mongoDB import MongoDB
import requests
import time


def get_topic(url, tagSet):
    
    r = requests.get(url + '1').text
    soup = BeautifulSoup(r, features="html.parser")
    s = soup.find_all('div', {"class":"group m-[10px] flex items-center"})
    for tag in s:
        tagName = tag.find('span').text
        tagSet.add(tagName)

def get_tag(data, tagName, tagDict):
    soup = BeautifulSoup(data, features="html.parser")
    s = soup.find_all('tbody', {"class":"reactable-data"})
    try:
        rows = s[0].find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            questNum = str(cells[1].text)
            if str(questNum) not in tagDict.keys():
                tagDict[str(questNum)] = []
            tagDict[str(questNum)].append(tagName)
    except Exception as e:
        print(f"Error with the tag name: {tagName}")
    finally:
        pass

def get_url(data, webDict, tagDict):

    soup = BeautifulSoup(data, features="html.parser")
    s = soup.find_all('div', {'role': 'row'})

    for i in range(1, len(s)):
        cell = s[i].find_all('div',{'role':'cell'})
        # link
        newDict = {}
        questPath = 'https://leetcode.com' + str(cell[1].find('a')['href'])
        # number and value
        questNum, questName = cell[1].find('a').text.split('. ')
        accptRate = cell[3].find('span').text
        hardType = cell[4].find('span').text
        topicList = []
        if str(i) in tagDict.keys():
            topicList = tagDict[str(i)]
        newDict['questionNo'] = questNum
        newDict['questionName'] = questName
        newDict['link'] = questPath
        newDict['accptRate'] = accptRate
        newDict['hardType'] = hardType
        newDict['types'] = '[' + ','.join(topicList) + ']' #topicList
        # newDict['likeHelp'] = {}
        # newDict['know'] = {}
        # newDict['neutral'] = {}
        # newDict['needHelp'] = {}
        if str(questNum) not in webDict.keys():
            webDict[str(questNum)] = newDict
        # webList.append([questNum, questName, questPath, accptRate, hardType, '[' + ','.join(topicList) + ']'])

if __name__ == '__main__':

    url = 'https://leetcode.com/problemset/all/?page='
    tagURL = 'https://leetcode.com/tag/'
    webDict = {}
    tagDict = {}
    tagSet = set()
    get_topic(url + '1', tagSet)
    # db = MongoDB()
    # db.connect_to_db(clusterName='studyDB', table='leetCodeDB')
    # tagSet = {'array'}
    for tag in tagSet:
        tag = tag.strip()
        tag = tag.lower()
        tag = tag.replace(' ', '-')
        tag = tag.replace('(', '')
        tag = tag.replace(')', '')
        tag = tag.replace('--', '-')
        print(f"Tag: {tag}")
        browser=webdriver.Firefox()
        browser.get(tagURL + str(tag) + '/')
        if 'array' in tag:
            time.sleep(10) 
        else:
            time.sleep(5)
        html = browser.page_source
        get_tag(html, tag, tagDict)
        browser.close()

    for page in range(1, 53):
        print(f"Page #{page}")
        browser=webdriver.Firefox()
        browser.get(url + str(page))
        time.sleep(5)
        html = browser.page_source
        get_url(html, webDict, tagDict)
        browser.close()

    file = open('items.txt','w')
    for num in webDict.keys():
        # db.insert_to_db(webDict[str(key)])
        newLine = ''
        for item in webDict[num].keys():
            newLine = newLine + webDict[num][item] + ';' 
        file.write(newLine+"\n")
    file.close()




