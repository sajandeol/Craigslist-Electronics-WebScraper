from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common import actions
from datetime import datetime
import os, smtplib, time, fileinput
from email.message import EmailMessage
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
BASE_URL = 'URL NEEDED TO GO TO CRAIGLIST SITE NEAR YOU'
fileLocation = "Location to store txtFile"
QUERY = 'electronic'
driver = webdriver.Chrome(options=options)

def outputResults(posts):
    print(f'{len(posts)} results containing: "{QUERY}"')
    with open(fileLocation, "w") as file:
        for i, post in enumerate(posts):
            titleDiv = post.find('a', class_ = 'result-title')
            postTitle = titleDiv.get_text()
            postURL = titleDiv.get('href')
            postTimeText = post.find('time').get('datetime')
            postTime = datetime.strptime(postTimeText, '%Y-%m-%d %H:%M')
            ellapsedMinutes = (datetime.now() - postTime)
            printText = (f'{i}: {postTitle}: {ellapsedMinutes}: {postURL}\n')
            print(printText)
            if(open(fileLocation, "r").read() != printText):
                file.writelines(printText)
                sendEmail()
            else:
                continue

def sendEmail():
    EMAIL_ADDRESS = 'USERS_EMAIL'
    EMAIL_PASS = 'PASSWORD TO YOUR EMAIL'
    EMAIL_SEND = 'RECIPIENT OF EMAIL'

    msg = EmailMessage()
    msg['Subject'] = 'Craiglist Posting?'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_SEND
    msg.add_attachment(open(fileLocation, "r").read(), filename ="Postings.txt")

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)

def stepThroughPages(posts, pageLink):
    driver.get(BASE_URL + pageLink)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    nextButton = soup.find('a', class_='next')
    posts.extend(soup.find_all('li', 'result-row'))

    if nextButton is None: return posts  
    return stepThroughPages(posts, nextButton.get('href'))


def doFunctions(test):
    count = 0
    while(count == 0): 
        outputResults(test)
        time.sleep(2)
        


totalPosts = stepThroughPages([], '/d/free-stuff/search/zip')
totalPosts = [post for post in totalPosts if QUERY in (post.find('a', class_='result-title').get_text().lower())]
doFunctions(totalPosts)
driver.quit()

