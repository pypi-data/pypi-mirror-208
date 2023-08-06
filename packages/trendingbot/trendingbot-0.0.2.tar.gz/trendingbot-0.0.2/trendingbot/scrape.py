

import urllib3
import requests
from bs4 import BeautifulSoup
import re
urllib3.disable_warnings()
headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
}

def re_select_element(html_str, element_type):
    regex = re.compile(r'<\s*(?P<element_type>%s).*?>(.*?)</\1>' % element_type, re.DOTALL)
    results = regex.findall(html_str)
    return [result[1] for result in results]
def re_select_class(html_str, class_name):
    regex = re.compile(r'<\s*%s.*?class\s*=\s*"(?P<class_name>%s)".*?>(.*?)</\1>' % (re.escape(class_name), class_name), re.DOTALL)
    results = regex.findall(html_str)
    return [result[2] for result in results]
def get_value(element, element_type):
    regex = re.compile(r'<%s.*?>(.*?)</%s>' % (element_type, element_type), re.DOTALL)
    match = regex.search(element)
    if match:
        return match.group(1)
def get_alink(html_str):
    links = []
    regex = re.compile(r'<a.*?href=["\'](?P<href>.*?)["\'].*?>')
    matches = regex.finditer(html_str)
    for match in matches:
        links.append(match.groupdict()['href'])
    return links
class HotTopic(object):
    def __init__(self,topic,type,content):
        self.topic=topic
        self.type=type
        self.content=content


def scrape_site(site):
    https = urllib3.PoolManager()
    response = https.request('GET', site.url, headers=headers)
    data=response.data.decode('utf8')
    tbody=re_select_element(data,'tbody')[0]
    trs=re_select_element(tbody,'tr')
    # _as=[HotTopic(f"{get_value(re_select_element(tr,'td')[1],'a')}",'None',get_alink(re_select_element(tr,'td')[1])) for tr in trs]
    topics=[HotTopic(f"{get_value(re_select_element(tr,'td')[1],'a')}",'None','https://tophub.today'+f"{get_alink(re_select_element(tr,'td')[1])[0]}") for tr in trs]
    return {'name':site.name,
            'trending_list':topics
    }








