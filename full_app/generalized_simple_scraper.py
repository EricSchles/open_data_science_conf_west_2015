import requests #sudo pip install requests 
import lxml.html #sudo pip install lxml.html
from unidecode import unidecode #sudo pip install unidecode

def links_grab(url):
    r = requests.get(url)
    html = lxml.html.fromstring(unidecode(r.text))
    return html.xpath("//a/@href") + [url] #ensures the url is stored in the final list

def crawl(base_url,start_depth=6):
    return crawler([base_url],base_url,start_depth)

def crawler(urls, base_url, depth):
    urls = list(set(urls))
    domain_name = base_url.split("//")[1].split("/")[0]
    url_list = []
    for url in urls:
        if domain_name in url:
            url_list += links_grab(url)
    print url_list
    url_list = list(set(url_list)) #dedup list
    url_list = [uri for uri in url_list if uri.startswith("http")]
    if depth > 1:
        url_list += crawler(url_list, base_url, depth-1)
    urls += url_list
    urls = list(set(urls))
    num_urls = len(urls)
    return url_list

if __name__ == '__main__':
    print crawl("https://hackingagainstslavery.github.io",6)
