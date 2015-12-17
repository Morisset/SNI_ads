'''
Created on 16 dec. 2015

@author: christophemorisset
'''
import ads
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

bibcode = '2014ApJ...784..173D'
res = ads.SearchQuery(q='citations(bibcode:{})'.format(bibcode), fl='author, title, year, pub, volume, page, bibcode')
papers = list(res)

# the following does not connect to ADS
for p in papers:
    print p.title
    
# the following DOES connect to ADS, because two papers have None as volume.
for p in papers:
    print p.volume

