#!/usr/bin/python

import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from collections import defaultdict
from urlparse import urlparse, urlunparse

parser=argparse.ArgumentParser()
parser.add_argument('-u', "--url", required=True)
parser.add_argument('-l', "--link-index", type=int, default=1)
group=parser.add_mutually_exclusive_group(required=True)
group.add_argument('-n', "--nfollows", type=int)
group.add_argument('-m', "--max-follows", type=int)
args=parser.parse_args()

class Crawler:

    class Node:
        def __init__(self,name):
            self.name=name
            self.edges=[]   # ints

        def add_edge(self,node_id):
            self.edges.append(node_id)

    def __init__(self):
        self.node_names=dict()   # name => int
        self.nodes=list()        # int => Node

    def make_node(self,name):
        if name not in self.node_names:
            node=Crawler.Node(name)
            self.nodes.append(node)
            self.node_names[name]=len(self.nodes)-1
        id=self.node_names[name]
        print('name=%s id=%d' % (name,id))
        return id

    def fix_link(self,link,current):
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

    def follow_link(self,source,n_follows,link_index):
        current=source
        iterations=0

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
                url=self.fix_link(link['href'],current)
                node_id=self.make_node(url)
                current=url
                print('%04d %s' % (iterations,current))

        return current

# -- start
p_url=urlparse(args.url)
url=urlunparse(['http',p_url.netloc,p_url.path,p_url.params,p_url.query,p_url.fragment])
crawler=Crawler()

if args.nfollows:
    sink=crawler.follow_link(source=url,n_follows=args.nfollows,link_index=args.link_index)
else:
    sink_count=defaultdict(int)
    source_to_sink=defaultdict(dict)

    for path_length in range(1,args.max_follows):
        sink=crawler.follow_link(source=url,n_follows=path_length,link_index=args.link_index)
        sink_count[sink]+=1
        source_to_sink[source][path_length]=sink
