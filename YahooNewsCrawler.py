
# coding: utf-8

# In[74]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import pymysql
import time


# In[75]:


def articles_DB(articles) : 
    table_name = keyword + "_articles"
    conn = pymysql.connect(host = "147.43.122.131", user = "root", password = "1234", charset = "utf8mb4")
    curs = conn.cursor()
    curs.execute("use yahoo_news ;")

    query = """CREATE TABLE IF NOT EXISTS """+ table_name + """ (ID int, URL text, Title varchar(200), Date varchar(50), Writer varchar(200), Provider varchar(200), Count int,Text text);"""
    curs.execute(query)

    query = """ALTER TABLE """ + table_name +""" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + table_name
    index = curs.execute(select_query)

    for value in articles :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        provider = value[4]
        count = value[5]
        content = value[6]

        query = """insert into """ + table_name + """(ID, URL, Title, Date, Writer, Provider, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,provider,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[76]:


def replies_DB(replies) :
    table_name = keyword + "_replies"
    conn = pymysql.connect(host = "147.43.122.131", user = "root", password = "1234", charset = "utf8mb4")
    curs = conn.cursor()
    curs.execute("use yahoo_news ;")
    
    query = """CREATE TABLE IF NOT EXISTS """+ table_name + """ (article_ID int, reply_ID int, reply_writer varchar(100),reply_date varchar(50),reply_body text, R_Like int, R_Bad int);"""
    curs.execute(query)

    query = """ALTER TABLE """ + table_name +""" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""
    curs.execute(query)

    conn.commit()
    
    for value in replies :
        article_ID = value[0]
        reply_ID = value[1]
        writer = value[2]
        date = value[3]
        content = value[4]
        like = value[5]
        bad = value[6]

        query = """insert into """ + table_name + """(article_ID, reply_ID, reply_writer, reply_date, reply_body, R_Like, R_Bad) values (%s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (article_ID, reply_ID, writer, date, content, like, bad))
        
        conn.commit()
        
    conn.close()
    print("FINISH")


# In[77]:


def rereplies_DB(rereplies) :
    table_name = keyword + "_rereplies"
    conn = pymysql.connect(host = "147.43.122.131", user = "root", password = "1234", charset = "utf8mb4")
    curs = conn.cursor()
    curs.execute("use yahoo_news ;")
    
    query = """CREATE TABLE IF NOT EXISTS """+ table_name + """ (article_ID int,reply_ID int, rereply_ID int, rereply_writer varchar(100),rereply_date varchar(50),rereply_body text, R_Like int, R_Bad int);"""
    curs.execute(query)

    query = """ALTER TABLE """ + table_name +""" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""
    curs.execute(query)

    conn.commit()

    select_query = """SELECT * from """ + table_name 
    index = curs.execute(select_query)
    
    for value in rereplies :
        article_ID = value[0]
        reply_ID = value[1]
        writer = value[2]
        date = value[3]
        content = value[4]
        like = value[5]
        bad = value[6]

        query = """insert into """ + table_name + """(article_ID, reply_ID, rereply_ID, rereply_writer, rereply_date, rereply_body, R_Like, R_Bad) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (article_ID, reply_ID, str(index), writer, date, content, like, bad))
    
        index = index + 1 
        
        conn.commit()
        
    conn.close()
    print("FINISH")


# In[78]:


def article_crawling() :
    articles = []
    URL_date_list = []
    page_num = 0
    article_ID = 0
    # 페이지 만큼 돌면서 링크 수집
    while True : 
        print(page_num)
        p_url = 'https://news.search.yahoo.com/search?p='+keyword+'&pz=10&fr=uh3_news_vert_gs&bct=0&b='+str(page_num)+'1'
        driver = webdriver.Chrome('./chromedriver/chromedriver',chrome_options=options)
        driver.implicitly_wait(3)
        driver.get(p_url)
        soup = BeautifulSoup(driver.page_source,'html.parser')

        a_tags = soup.select('h4 > a')
            
        # 한 페이지에 있는 링크들 전부 가져오기
        for a in a_tags :
            if 'href' in a.attrs :
                if 'news.yahoo.com' in a.attrs['href'] :
                    url = a.attrs['href']
                    driver = webdriver.Chrome('./chromedriver/chromedriver',chrome_options=options)
                    driver.implicitly_wait(3)
                    driver.get(url)

                    soup = BeautifulSoup(driver.page_source,'html.parser')
                    news_title = soup.select('header')[0].text.replace('\n','')
                    news_date = soup.find("time", {"itemprop" : "datePublished"}).text
                    # writer가 존재하지 않으면 값을 none으로
                    if soup.find("div", {"itemprop" : "author creator"}) is not None :
                        news_writer = soup.find("div", {"itemprop" : "author creator"}).text
                    else : 
                        news_writer = "None";
                    # provider가 존재하지 않으면 값을 none으로
                    if soup.find("span", {"class" : "provider-link"}) is not None :
                        news_provider = soup.find("span", {"class" : "provider-link"}).text
                    else : 
                        news_provider = "None";

                    # 댓글 위치에 따라 다르게
                    if soup.find("div", {"class" : "Trsdu(.2s) Trsp(scale) Scale(1)"}) is not None :
                        if soup.find("div", {"class" : "Trsdu(.2s) Trsp(scale) Scale(1)"}).text == '' :
                            reply_count = 0
                        else :
                            reply_count = soup.find("div", {"class" : "Trsdu(.2s) Trsp(scale) Scale(1)"}).text
                    elif soup.find("div", {"class" : "comments-body"}) is not None : # 정규식으로 괄호 안 값 추출
                        if(soup.find("div", {"class" : "comments-body"}).select('div > div > div')[0].text.find('(') != -1) :
                            temp = soup.find("div", {"class" : "comments-body"}).select('div > div > div')[0].text
                            reply_count = re.search(r'\((.*?)\)',temp).group(1)
                    else : 
                        reply_count = 0
                    news_content = soup.find("article", {"itemprop" : "articleBody"}).text.replace('\n','').strip()
                    articles.append([article_ID,url,news_title,news_date,news_writer,news_provider,reply_count,news_content])
                    if reply_count != 0 :
                        reply_crawling(driver,article_ID)
                    else :
                        print("댓글 없음")
                    article_ID += 1
                    
        driver.get(p_url)
        page_num += 1
        # 다음 페이지 버튼 있나 확인 후 없으면 while문 빠져나감
        try :
            driver.find_element_by_xpath("//a[@class='next']").click()
        except : 
            break;
   
    articles_DB(articles) # 기사들 디비에 저장
    print("기사 수집 완료")


# In[79]:


#DB 생성시 이용
conn = pymysql.connect(host = "147.43.122.131", user = "root", password = "1234", charset = "utf8mb4")
curs = conn.cursor()
query = """CREATE DATABASE yahoo_news default CHARACTER SET utf8mb4;"""
curs.execute(query)


# In[80]:


def reply_crawling(driver,article_ID) :
    soup = BeautifulSoup(driver.page_source,'html.parser')
    #댓글 보라색 버튼이 없는 경우는 댓글보기 누르고 
    if soup.find("div", {"class" : "Trsdu(.2s) Trsp(scale) Scale(1)"}) is None :
        driver.find_element_by_xpath("//button[@class='comments-title D(ib) Td(n) Bd(0) P(0) Fw(b) Fz(16px) Cur(p) C(#000)']").click() 
    # show more 버튼 존재하면 클릭   
    try :
        show_more = driver.find_element_by_xpath("//div[@class='comments-body']/button") 
        # 댓글 보라색 버튼이 있는 경우/없는 경우 show-more 계속 누름
        while True :
            try :
                show_more.click()
                time.sleep(2)
            except :
                break
    except :
        print("show-more 버튼 없음")
    
    # 위치 벗어나는 오류 발생하므로 스크롤 위로 당겨줌
    driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    
    soup = BeautifulSoup(driver.page_source,'html.parser')
    replies = []
    reply_ID = 0
    reply_list = soup.findAll("li", {"class" : "comment Pend(2px) Mt(5px) P(12px) "})
    for li in reply_list :
        reply_writer = li.find("div", {"class" : "Fz(13px) Mend(20px)"}).find("button").text
        reply_date = li.find("div", {"class" : "Fz(13px) Mend(20px)"}).find("span").text
        reply_body = li.find("div", {"class" : "Wow(bw)"}).text
        # 댓글 좋아요 나빠요
        temp = li.find("div", {"class" : "D(ib) Pos(r)"}).findAll("button")
        reply_Like = temp[0].text
        reply_Bad = temp[1].text
        if reply_Like == "" :
            reply_Like = 0
        if reply_Bad == "" :
            reply_Bad = 0    
        replies.append([article_ID,reply_ID,reply_writer,reply_date,reply_body,reply_Like,reply_Bad])
        rereply_crawling(driver,li,article_ID,reply_ID) # 대댓글 수집
        reply_ID += 1

    replies_DB(replies) #DB에 저장
    print("댓글 수집 완료")


# In[81]:


def rereply_crawling(driver,li,article_ID,reply_ID) :
    if li.find("button", {"class" : "replies-button O(n):h O(n):a P(0) Bd(n) Cur(p) Fz(12px) Fw(500) C($c-fuji-grey-g) D(ib) Mend(20px)"}) is not None :
        # rereply 열기
        driver.find_element_by_xpath("//ul[@class='comments-list List(n) Ovs(touch) Pos(r) Mstart(-12px) Pt(5px)']/li["+str(reply_ID+1)+"]/div/div[4]/div/button[2]").click()
        time.sleep(3) # 클릭 후 로딩 되어야 하므로 3초정도 여유
        # rereply 더 많아서 show more해야하면
        try :
            show_older_replies = driver.find_element_by_xpath("//button[@class='show-next-button Fz(14px) Fw(b) C($c-fuji-blue-1-a) Bd(0) P(0) Mx(0) Mt(10px) Mb(5px) Mstart(40px)']") 
            while True :
                try :
                    show_older_replies.click()
                    time.sleep(2)
                except :
                    break
        except :
            print("show_older_replies 버튼 없음")
          
        # 위치 벗어나는 오류 발생하므로 스크롤 위로 당겨줌
        driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
        soup = BeautifulSoup(driver.page_source,'html.parser')
        
        rereplies = []
        rereply_list = soup.find("div", {"class" : "reply-box"}).findAll("li", {"class" : "comment Pend(2px) Py(10px) Pstart(10px) "})
        
        for i in rereply_list :
            rereply_writer = i.find("div", {"class" : "Fz(13px) Mend(20px)"}).find("button").text
            rereply_date = i.find("div", {"class" : "Fz(13px) Mend(20px)"}).find("span").text
            rereply_body = i.find("div", {"class" : "Wow(bw)"}).text
             # 댓글 좋아요 나빠요
            temp = i.find("div", {"class" : "D(ib) Pos(r)"}).findAll("button")
            rereply_Like = temp[0].text
            rereply_Bad = temp[1].text
            if rereply_Like == "" :
                rereply_Like = 0
            if rereply_Bad == "" :
                rereply_Bad = 0    
            rereplies.append([article_ID,reply_ID,rereply_writer,rereply_date,rereply_body,rereply_Like,rereply_Bad])
       
        # 위치 벗어나는 오류 발생하므로 스크롤 위로 당겨줌
        driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    
        # 다시 rereply 닫음
        driver.find_element_by_xpath("//ul[@class='comments-list List(n) Ovs(touch) Pos(r) Mstart(-12px) Pt(5px)']/li["+str(reply_ID+1)+"]/div/div[4]/div/button[2]").click()
        time.sleep(3) # 클릭 후 로딩 되어야 하므로 3초정도 여유
        rereplies_DB(rereplies) #DB에 저장
        print("대댓글 수집 완료")
    else :
        print("대댓글 없음")


# In[ ]:


options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument("--start-maximized")
keyword = input("Keyword ? ")
article_crawling() # 기사 수집 시작
