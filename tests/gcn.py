import requests
import re

def cite(num):
    s = requests.get('https://gcn-circular-gateway.herokuapp.com/gcn-bib/bynumber/%i'%num).text
    return re.search('@ARTICLE\{(.*?),', s).groups()[0]
