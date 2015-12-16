# coding: utf-8
'''
Created on 14 dec. 2015

@author: christophemorisset

VERSION 3.1
'''


import ads
import requests.packages.urllib3
from unidecode import unidecode as uni

requests.packages.urllib3.disable_warnings()

#cv = lambda str: unicode(str).encode('utf8')
cv = lambda str: uni(str).replace('$', '').replace('#', '').replace('&', '')
    

def pretty_author_name(authors):
    aspl = authors.split(",")
    aspl = [a for a in aspl if a != u'']
    if len(aspl) > 1:
        res1 = aspl[0]
        if aspl[1].strip() != '':
            res2 = aspl[1].strip()[0]
        elif aspl[2].strip() != '':
            res2 = aspl[2].strip()[0]
        else:
            res2 = ''
        return  "{}, {}.".format(cv(res1), cv(res2) )
    else:
        return authors

def auts(p):
    if len(p.author) > 5:
        auts = ', '.join([pretty_author_name(a) for a in p.author][0:5]) + ' et al.'
    else:
        auts = ', '.join([pretty_author_name(a) for a in p.author])
    return auts
   
def pretty_ref(p, with_title=False):
    try:
        year = ', {}'.format(cv(p.year))
    except:
        year = ''
    try:
        pub = ', {}'.format(cv(p.pub))
    except:
        pub = ''
    try:
        volume = ', {}'.format(cv(p.volume))
    except:
        volume = ''
    try:
        page = ', {}'.format(cv(p.page[0]))
    except:
        page = ''
    if with_title:
        try:
            title = ', {{\it {}}}'.format(cv(p.title[0]))
        except:
            title = ''
    else:
        title = ''
        
    return('{}{}{}{}{}{}'.format(auts(p), year, title, pub, volume, page))
           
def get_papers(author):
    
    res = ads.SearchQuery(author=author, 
                          fl='author, title, year, pub, volume, page, citation, citation_count, bibcode')
    try:
        papers = list(res)
        print('Got {} papers for {}'.format(len(papers), author))
    except:
        papers = None
        print('No papers')
    return papers

def get_citations(papers):
    
    citations = {}
    if papers is not None:
        for p in papers:
            N_citations = p.citation_count
            if N_citations > 0:
                res = ads.SearchQuery(q='citations(bibcode:{})'.format(p.bibcode), 
                                      fl='author, title, year, pub, volume, page, citation, citation_count, bibcode')
                citations[p.bibcode] = list(res)
                print('Got {} citations for paper {}.'.format(N_citations, p.bibcode))
    return citations

def print_results(author, papers, citations, filename=None):
    token = ads.config.token # store the token
    ads.config.token = '' # we don't need to connect to ads from now (but it we allow it, it will...)
    if filename is None:
        def myprint(str):
            print(str)
    elif type(filename) is file:
        f = filename
        def myprint(str):        
            f.write(str + '\n')
    else:
        f = open(filename)
        def myprint(str):        
            f.write(str + '\n')
    
    myprint('\\documentclass{letter}')
    myprint('\\begin{document}')
    myprint('\\begin{enumerate}')
    for p in sorted(papers , key=lambda pp: (pp.year, pp.author[0])):
        typeA = [] # no autocitas
        typeB = [] # autocitas por coauthor
        typeC = [] # autocita
        N_citations = p.citation_count
        authors = [pretty_author_name(a) for a in p.author]
        if N_citations > 0:
            for citing in citations[p.bibcode]:
                autocite = False
                autociteco = False
                for this_author in citing.author:
                    if uni(pretty_author_name(this_author)) == uni(pretty_author_name(author)):
                        autocite = True
                    elif uni(pretty_author_name(this_author)) in [uni(a) for a in authors]:
                        autociteco = True
                if autocite:
                    typeC.append(citing)
                elif autociteco:
                    typeB.append(citing)
                else:
                    typeA.append(citing)
            if len(typeA) + len(typeB) > 0:
                myprint('\item {} \\\ Total = {}, Type A = {}, type B = {}, type C = {} \\\ '.format(pretty_ref(p, with_title=True), 
                                                                                                     p.citation_count,
                                                                                                     len(typeA), len(typeB), len(typeC)))
                if len(typeA) > 0:
                    myprint('{\\bf Citations Type A:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeA , key=lambda pp: (pp.year, pp.author[0])):
                        myprint('\item {}'.format(pretty_ref(pc)))
                    myprint('\end{itemize}')
                if len(typeB) > 0:
                    myprint('{\\bf Citations Type B:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeB , key=lambda pp: (pp.year, pp.author[0])):
                        myprint('\item {}'.format(pretty_ref(pc)))
                    myprint('\end{itemize}')
                myprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    myprint('\\end{enumerate}')
    myprint('\end{document}')
    if filename is not None and type(filename) is not file:
        f.close()
    ads.config.token = token # redefine the token as it was when entering


def do_all(author):
    articulos = get_papers(author)
    citas = get_citations(articulos)
    print_results(author, articulos, citas)
    f = open('misrefs_{}.tex'.format(author), 'w')
    print_results(author, articulos, citas, f)
    f.close()

"""
ads.config.token = "5KAUJBW123456789dHCzvJWn73WyKVvNvyugC87M" # this one is fake, you need to use your own token
author = 'Morisset, C.'             
articulos = get_papers(author)
citas = get_citations(articulos)
print_results(author, articulos, citas)
f = open('misrefs.tex', 'w')
print_results(author, articulos, citas, f)
f.close()
"""
