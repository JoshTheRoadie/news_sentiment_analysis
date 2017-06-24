import requests
import time
from collections import namedtuple
from bs4 import BeautifulSoup
from textblob import TextBlob


RawArticle = namedtuple('RawArticle', 'publisher title article')
BlobArticle = namedtuple('BlobArticle', 'publisher title polarity subjectivity')


def get_html(url):
    response = requests.get(url)
    return response.text


def get_links(start_url, page_num_offset, time_delay, get_link_func, num_pages=1):
    links = []
    for page in range(num_pages):
        url = (start_url.format(page + page_num_offset))
        links.extend(get_link_func(get_html(url)))
        time.sleep(time_delay)
    return links


def get_breitbart_links(html):
    pass


def get_mother_jones_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    article_list = soup.find_all(class_='views-field views-field-title')
    links = []
    for item in article_list:
        partial_url = item.find('a').get('href')
        links.append('http://www.motherjones.com{}'.format(partial_url))
    return links


def get_fox_links(html):
    pass


def scrape_breitbart(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find(id='MainW')
    story = article.find_all('p')
    text = []
    for item in story:
        text.append(item.get_text())
    return RawArticle(publisher=u'Breitbart', title=soup.title.get_text(), article=' '.join(text))


def scrape_fox(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find(class_='article-text')
    story = article.find_all('p')
    text = []
    for item in story:
        text.append(item.get_text())
    return RawArticle(publisher=u'Fox News', title=soup.title.get_text(), article=' '.join(text))


def scrape_mother_jones(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find(id='node-body-top')
    story = article.find_all('p')
    text = []
    for item in story:
        text.append(item.get_text())
    return RawArticle(publisher=u'Mother Jones', title=soup.title.get_text(), article=' '.join(text))


def blob_raw_article(raw_article):
    blob = TextBlob(raw_article.article)
    sentiment = blob.sentiment
    return BlobArticle(publisher=raw_article.publisher,
                       title=raw_article.title,
                       polarity=sentiment.polarity,
                       subjectivity=sentiment.subjectivity)


def analyze_articles(links):
    blobs = []
    for link in links:
        blobs.append(blob_raw_article(scrape_mother_jones(get_html(link))))
        time.sleep(10)
    return blobs

SITE_CONFIGS = {
    'Mother Jones': {'start_url': 'http://www.motherjones.com/politics?page={}',
                     'page_offset': 0,
                     'delay': 10,
                     'link_func': get_mother_jones_links,
                     'scrape_func': scrape_mother_jones},
    'Breitbart': {'start_url': 'http://www.breitbart.com/big-government/page/{}/',
                  'page_offset': 1,
                  'delay': 10}
}


if __name__ == "__main__":
    mj = SITE_CONFIGS['Mother Jones']
    stories = get_links(mj['start_url'], mj['page_offset'], mj['delay'], mj['link_func'])
    print len(stories)
    for story in stories:
        print story
    # with open('breitbart_news.html', 'r') as news_doc:
    #     html_doc = news_doc.read()
    # raw = scrape_breitbart(html_doc)
    # print blob_raw_article(raw)
