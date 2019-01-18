import random
import re
import time
import pymongo
import requests
from lxml import etree
from pprint import pprint

from config import *

url = 'https://weixin.sogou.com/weixin'
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]


# 获取代理
def get_proxy():
    return requests.get('http://127.0.0.1:5010/get/').text
# 删除代理
def delete_proxy(proxy):
    requests.get('http://127.0.0.1:5010/delete/?proxy={}'.format(proxy))

# 获取索引页面
def get_index_page(page, keyword):
    try:
        print('正在爬取%d页' % page)
        proxy = get_proxy()
        proxies = {"http": "http://{}".format(proxy)}
        headers1 = {
            'User-Agent': random.choice(USER_ANGENT),
            'Host': 'weixin.sogou.com',
            'Cookie': random.choice(COOKIES),
            'Upgrade-Insecure-Requests': '1'
        }
        data = {
            'type': '2', # 2为文章，1为公众号
            'query': keyword,
            'ie': 'utf8',
            'page': page
        }
        response = requests.get(url=url, headers=headers1, params=data, proxies=proxies, allow_redirects=False,timeout=5)   # allow_redirects=False，禁止重定向
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:  # 状态码302为重定向，跳转至输入验证码的页面
            print('爬虫被检测，更换代理和cookie,重新爬取')
            return get_index_page(page, keyword)
    except ConnectionError:
        print('索引页面连接出现错误，重新访问')
        return get_index_page(page, keyword)


# 获取文章链接
def get_detail_link(html):
    html = etree.HTML(html)
    items = html.xpath('//div[@class="main-left"]//ul[@class="news-list"]/li')
    for item in items:
        link = item.xpath('.//div[@class="txt-box"]/h3/a/@href')[0]
        get_content(link=link)


# 获取文章
def get_content(link):
    proxy = get_proxy()
    proxies = {"http": "http://{}".format(proxy)}
    try:
        headers2 = {
            'User-Agent': random.choice(USER_ANGENT),
            'Host': 'mp.weixin.qq.com',
            'Cookie': random.choice(COOKIES),
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url=link, headers=headers2, proxies=proxies,timeout=3)
        time.sleep(3)   # 延时3s
        html = etree.HTML(response.text)
        # 标题
        title = html.xpath('//div[@id="img-content"]/h2[@class="rich_media_title"]/text()')[0].strip()
        # 公众号
        wechat = html.xpath('//div[@id="img-content"]/div[@id="meta_content"]/span[@id="profileBt"]/a[@id="js_name"]/text()')[0].strip()
        # 文章内容
        content = ''.join(html.xpath('//div[@class="rich_media_content "]//text()')).strip()
        content = re.sub(r'\s', '', content)    # 去除空白字符
        article = {
            '标题': title,
            '公众号': wechat,
            '内容': content
        }
        pprint(article)
        save_to_mongoDB(article=article)
    except IndexError :
        print('文章索引错误，错误连接为：', link)  # 索引出现错误多半是因为文章为转载，无文本内容。
    except  requests.exceptions.ConnectionError:    # HTTPConnectionPool错误为代理ip有问题，重试即可。
        print('获取文章出现异常,重试,删除无效代理', proxy)
        delete_proxy(proxy=proxy)    # 删除无效代理
        return  get_content(link)
    except requests.exceptions.ReadTimeout:
        print('获取文章超时，重试')
        return  get_content(link)
    except Exception as e:
        print('出现其他异常',e)


# 保存文章
def save_to_mongoDB(article):
    # 根据文章标题去重
    if db[MONGO_TABLE].update({'标题': article['标题']}, {'$set': article}, True):
        print('保存至mongoDB', article['标题'])
    else:
        print('保存出错')


def main():
    print('爬取开始，正在为您搜索的关键字为--->%s' % KEYWORD)
    for page in range(1, MAX_PAGE + 1):
        html = get_index_page(page=page, keyword=KEYWORD)
        get_detail_link(html=html)


if __name__ == '__main__':
    main()
