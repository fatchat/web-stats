import os
import sys
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
from urlparse import urlparse, urlunparse

def fix_link(link,current):
    p_link=urlparse(link)    
    if p_link.scheme!='':
        return link
    # no scheme, assume http
    if p_link.netloc!='':
        return 'http:' + link
    # no netloc, get from current
    p_current=urlparse(current)
    if p_current.netloc=='':
        raise Exception('no netloc for current! %s' % current)
    return urlunparse(['http',p_current.netloc,p_link.path,p_link.params,p_link.query,p_link.fragment])

def follow_link(source,n_follows,link_index):
    current=source
    iterations=0
    seen=set(source)
    while iterations < n_follows:
        iterations+=1
        r=requests.get(current)
        if r.ok:
            soup=BeautifulSoup(r.text)
            links=soup.findAll('a')
            if len(links)==0: break
            for li in range(min(link_index,len(links)),len(links)):
                link=links[li-1]
                if link.has_attr('href'):
                    break
                link=None
            if link==None: break
            url=fix_link(link['href'],current)
            if url in seen:
                print('** already seen %s' % url)
                break
            current=url
            seen.add(url)
            print('%04d %s' % (iterations,current))

    return current

sink_count=defaultdict(int)
source_to_sink=defaultdict(dict)
source='http://en.wikipedia.org/' if len(sys.argv)<1 else sys.argv[1]

for path_length in range(1,100):
    sink=follow_link(source=source,n_follows=path_length,link_index=10)
    sink_count[sink]+=1
    source_to_sink[source][path_length]=sink
