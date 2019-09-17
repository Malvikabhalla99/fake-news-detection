from datetime import datetime 
from datetime import date
from bs4 import BeautifulSoup 
from urllib.request import urlopen as uReq
import json
import requests

file = "fake_news_dataset_india.csv"
fr = open (file,"a+")

def facebook_post_extractor(soup):
    containers  = soup.find_all("div",{"class" : "section1"})
    container = containers[0]
    # search for fb post
    if container.find("div",{"data-title" : "Facebook"}) is not None:
        facebook_count = 1
        ct = container.find("div",{"data-title" : "Facebook"})
        facebook_link = ct.cdata.iframe['src']
        print(facebook_link) #4
        return facebook_link
    else :
        return ""
    
def twitter_link_extractor(soup):
    containers  = soup.find_all("div",{"class" : "section1"})
    container = containers[0]
    # search for fb post
    if container.find("div",{"data-type" : "twitter"}) is not None:
        twitter_count = 1
        ct = container.find("div",{"data-type" : "twitter"})
        twitter_link = ct.div.blockquote.a['href']
        print(twitter_link) #4  
        return twitter_link
    else :
        return ""

def image_link_extractor(soup):
    containers  = soup.find_all("div",{"class" : "section1"})
    container = containers[0]
    # search for img 
    if container.find("div",{"class" : "image"}) is not None :
        con = container.find("div",{"class" : "image"})
        ans_img = con.img['src']
        print (ans_img) 
        return ans_img
    else :
        return ""
    
def extract_data(s,soup,url):
    siteName = "Times of India" #1
    link = url #2
    twitter_count = 0
    facebook_count = 0
    image_count = 0
    twitter_link = ""
    facebook_link =""
    ans_img =""
    fbtext = "facebook.com"
    twittertext = "twitter.com"
    date = ""
    claim = ""
    try:
       date = json.loads(s.text)['datePublished'] #3
       claim = json.loads(s.text)['claimReviewed'] #4
       
       if json.loads(s.text)['itemReviewed']['author'] is not None :
           data =  json.loads(s.text)['itemReviewed']['author']
           text_present  = data.get('sameAs')
           
           if text_present :
               print(text_present)
               if text_present.find(fbtext) != -1:
                   facebook_count = 1
                   facebook_link = text_present
                   print(facebook_link)
            
               if text_present.find(twittertext) != -1:
                   twitter_count = 1
                   twitter_link = text_present
                   print(twitter_link)
        
       if facebook_count == 0 :
           facebook_link = facebook_post_extractor(soup)
                   
       if twitter_count == 0 :
           twitter_link = twitter_link_extractor(soup)
        
       if image_count == 0 :
           ans_img = image_link_extractor(soup)
            
       row = siteName + "," + link + "," + date + "," + str(claim) + "," + twitter_link + "," + facebook_link + "," + ans_img + "\n"
       fr.write(row)
       return row
    
    except (ValueError, KeyError) :
        print("error")
        return False
                
   
def date_extractor(soup):
    date_found = soup.find_all("time")
    date = date_found[0]['datetime']
    print(date)
    return date

def claim_extractor(soup):
    claim_found = soup.find_all("div",{"class" : "artsyn"})
    claims = claim_found[0].text
    return claims
    '''
    claim_found = soup.find_all("artsummary")
    claims = ""
    if claim_found[0].ul is not None :
        claims = claim_found[0].ul.li.text
    else :
        if claim_found[0].ol is not None :
            claims = claim_found[0].ol.li.text
    print(claims)
    return claims
    '''    
    

def read_intext(url):
   r= requests.get(url)
   siteName = "Times of India" #1
   link = url #2
   date = ""
   claim = ""
   print(url)
   soup = BeautifulSoup(r.text, 'html.parser')
   s = soup.find('script', type='application/ld+json')
   
   ans = extract_data(s,soup,url)
   
   if ans == False :
       
       #date and claim would have not been set
       date = date_extractor(soup)
       claim = claim_extractor(soup)
       # extract the twitter , facebook and image links
       facebook_link = facebook_post_extractor(soup)
       twitter_link = twitter_link_extractor(soup)
       ans_img = image_link_extractor(soup)
       
       row = siteName + "," + link + "," + date + "," + str(claim) + "," + str(twitter_link) + "," + str(facebook_link) + "," + str(ans_img) + "\n"
       fr.write(row)


def convertToDate(text):
    text = text.split(', ')[0]
    date_obj = datetime.strptime(text, '%d %b %Y')
    date_obj = date_obj.strftime('%d %m %Y')
    today = date.today()
    d1 = today.strftime("%d %m %Y")
    date_format = "%d %m %Y"
    a = datetime.strptime(date_obj, date_format)
    b = datetime.strptime(d1, date_format)
    delta = b - a
    if delta.days <=21 :
        return True
    else:
        return False


def read_pages(i):
    if i==1 :
        url = "https://timesofindia.indiatimes.com/times-fact-check"
    else :
        url = "https://timesofindia.indiatimes.com/times-fact-check/" + str(i)
    
    uClient = uReq(url)
    page_html = uClient.read()
    page_soup = soup(page_html,"html.parser")

    containers = page_soup.find_all("ul",{"class" : "list5 clearfix"})
    
    for container in containers[0].find_all('li') :
        if container.find("span"):
            url_to_news  = container.span.a["href"]
            next_url = "https://timesofindia.indiatimes.com" + url_to_news
            if container.find("span",{"class" : "w_bylinec"}):
                valid = container.find("span",{"class" : "w_bylinec"})
                valid_or_not = valid.text
                if convertToDate(valid_or_not) == True :
                    read_intext(next_url)
            
         
    second_containers = page_soup.find_all("ul",{"class" : "top-newslist clearfix"})
    for container in second_containers[0].find_all('li'):
        if container.find("span"):
            url_to_news  = container.span.a["href"] 
            next_url = "https://timesofindia.indiatimes.com" + url_to_news
            if container.find("span",{"class" : "w_bylinec"}):
                valid = container.find("span",{"class" : "w_bylinec"})
                valid_or_not = valid.text
                if convertToDate(valid_or_not) == True :
                   read_intext(next_url)
            
           
          
read_pages(1)
   
   
   
   
