# coding: utf-8
'''
Created on 14 dec. 2015

@author: christophemorisset
'''


import ads
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

cv = lambda str: unicode(str).encode('utf8')

def pretty_author_name(authors):
    aspl = authors.split(",")
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
   
def pretty_ref(p):
    if cv(p.year) is not None:
        year = ', {}'.format(cv(p.year))
    else:
        year = ''
    if cv(p.pub) is not None:
        pub = ', {}'.format(cv(p.pub))
    else:
        pub = ''
    if cv(p.volume) is not None:
        volume = ', {}'.format(cv(p.volume))
    else:
        volume = ''
    try:
        page = ', {}'.format(cv(p.page[0]))
    except:
        page = ''
        
    return('{}{}{}{}{}'.format(auts(p), year, pub, volume, page))
           
def get_papers(author):
    
    res = ads.SearchQuery(author=author)
    try:
        papers = list(res)
        print('Got {} papers for {}'.format(len(papers), author))
    except:
        print('No papers')
    return papers

def get_citations(papers):
    
    citations = {}
    if papers is not None:
        for p in papers:
            N_citations = p.citation_count
            if N_citations > 0:
                citations[p.bibcode] = []
                for citation in p.citation:
                    citations[p.bibcode].append(ads.SearchQuery(bibcode=citation).next())
                print('Got {} citations for paper {}.'.format(N_citations, p.bibcode))
    return citations

def print_results(author, papers, citations, filename=None):
    
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
    
    for p in sorted(papers , key=lambda pp: pp.year):
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
                    if pretty_author_name(this_author) == pretty_author_name(author):
                        autocite = True
                    elif pretty_author_name(this_author) in authors:
                        autociteco = True
                if autocite:
                    typeC.append(citing)
                elif autociteco:
                    typeB.append(citing)
                else:
                    typeA.append(citing)
            myprint('{} \\\ Total = {}, Type A = {}, type B = {}, type C = {}'.format(pretty_ref(p), p.citation_count,
                                                                                      len(typeA), len(typeB), len(typeC)))
            if len(typeA) > 0:
                myprint('{\\bf Citations Type A:}')
                myprint('\\begin{itemize}')
                for pc in typeA:
                    myprint('\item {}'.format(pretty_ref(pc)))
                myprint('\end{itemize}')
            if len(typeB) > 0:
                myprint('{\\bf Citations Type B:}')
                myprint('\\begin{itemize}')
                for pc in typeB:
                    myprint('\item {}'.format(pretty_ref(pc)))
                myprint('\end{itemize}')
            myprint('\\hline')
            myprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    myprint('\end{document}')
    if filename is not None and type(filename) is not file:
        f.close()



"""
ads.config.token = "5KAUJBW123456789dHCzvJWn73WyKVvNvyugC87M"
author = 'Morisset, C.'             
articulos = get_papers(author)
citas = get_citations(articulos)
print_results(author, articulos, citas)
f = open('misrefs.tex', 'w')
print_results(author, articulos, citas, f)
"""