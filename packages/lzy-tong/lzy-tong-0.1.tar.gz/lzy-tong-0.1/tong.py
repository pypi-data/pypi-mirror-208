import time
from json import loads
from urllib import request
from bs4 import BeautifulSoup


def tong(*args):
    return int(time.mktime(time.strptime(loads(
        BeautifulSoup(request.urlopen(F"https://booting.lofter.com/post/{args[0]}"), 'html.parser').select_one(
            'div.txt > p').text).get(args[1]), "%Y-%m-%d %H:%M:%S"))) - int(time.mktime(
        time.strptime(request.urlopen('https://www.baidu.com').headers['date'][5:25], "%d %b %Y %H:%M:%S")) + 28800)
