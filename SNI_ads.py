#!/usr/bin/env python
'''
Created on 14 dec. 2015

@author: christophemorisset

'''


import ads
import requests.packages.urllib3
from unidecode import unidecode as uni
import argparse

__version__ = "4.4"

requests.packages.urllib3.disable_warnings()
MAX_pages = 1000
MAX_papers = 1000000

#cv = lambda str: unicode(str).encode('utf8')
cv = lambda str: uni(str).replace('$', '').replace('#', '').replace('&', '').replace('_', '\_')
    
clean_author = lambda author: ''.join([s for s in author if s not in ('.', ' ', ',')])

def pretty_author_name(authors):
    """
    Returns the author name in the form Smith, J.
    """
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
    """
    Returns p.author in the form of a string with a maximum of 5 authors (if more, uses et al.)
    """
    
    if len(p.author) > 5:
        auts = ', '.join([pretty_author_name(a) for a in p.author][0:5]) + ' et al.'
    else:
        auts = ', '.join([pretty_author_name(a) for a in p.author])
    return auts
   
def pretty_ref(p, with_title=False):
    """
    Returns a string in the form
    authors, year, {\it title}, pub, volume, page
    by default, title is not included. Changed by with_title keyword.
    type(p) is ads.search.Article
    """
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
        #volume=''
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
           
def get_papers(author, max_papers=None):
    """
    Returns a list of all the papers from author that contain at least one citation.
    max_paper can reduce the number of papers. The default is MAX_papers (1000000)
    author is a string.
    The papers are ads.search.Article
    """
    if max_papers is None:
        max_papers = MAX_papers
    res = ads.SearchQuery(author=author, 
                          fl='author, title, year, pub, volume, page, citation, citation_count, bibcode',
                          max_pages=MAX_pages)
    try:
        papers = list(res)
    except:
        papers = None
    papers = [p for p in papers if p.citation_count > 0][0:max_papers]
    # The following to resolve a bug when Volume is undefined
    for ppp in papers:
        if "volume" not in ppp.__dict__.keys():
            ppp.__dict__['volume'] = None
            ppp.__dict__['_raw'][u'volume'] = None
    print('Got {} papers from {} with at least one citation'.format(len(papers), author))
    return papers

def get_citations(papers):
    """
    papers: list of ads.search.Article
    Returns a dictionnary where each key corresponds to the bibcode of one element of papers and the value is a list of 
    papers citing the given paper.
    """
    citations = {}
    if papers is not None:
        for p in sorted(papers , key=lambda pp: (pp.year, pp.author[0])):
            N_citations = p.citation_count
            if N_citations > 0:
                res = ads.SearchQuery(q='citations(bibcode:{})'.format(p.bibcode), 
                                      fl='author, title, year, pub, volume, page, bibcode',
                                      max_pages=MAX_pages)
                citas = list(res)
                # The following to resolve a bug when Volume is undefined
                for ppp in citas:
                    if "volume" not in ppp.__dict__.keys():
                        ppp.__dict__['volume'] = None
                        ppp.__dict__['_raw'][u'volume'] = None
                citations[p.bibcode] = citas
                print('Got {} citations for paper {}.'.format(N_citations, p.bibcode))
    return citations

def print_results(author, papers, citations, filename=None):
    """
    Print the results on the screen and in a file.
    """
    #token = ads.config.token # store the token
    #ads.config.token = '' # we don't need to connect to ads in this function (but it we allow it, it will...)
    if filename is None:
        def myprint(str):
            print(str)
    elif type(filename) is file:
        f = filename
        def myprint(str):        
            f.write(str + '\n')
    else:
        f = open(filename, 'w')
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
                myprint('\\item {} \\\ Total = {}, Type A = {}, type B = {}, type C = {} \\\ '.format(pretty_ref(p, with_title=True), 
                                                                                                     p.citation_count,
                                                                                                     len(typeA), len(typeB), len(typeC)))
                if len(typeA) > 0:
                    myprint('{\\bf Citations Type A:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeA , key=lambda pp: (pp.year, pp.author[0])):
                        myprint('\\item {}'.format(pretty_ref(pc))) #this one!!!
                    myprint('\\end{itemize}')
                if len(typeB) > 0:
                    myprint('{\\bf Citations Type B:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeB , key=lambda pp: (pp.year, pp.author[0])):
                        myprint('\\item {}'.format(pretty_ref(pc))) #this one!!!
                    myprint('\\end{itemize}')
                myprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    myprint('\\end{enumerate}')
    myprint('\\end{document}')
    if filename is not None and type(filename) is not file:
        f.close()
    #ads.config.token = token # redefine the token as it was when entering

def do_all(author, max_papers=None, no_screen=False, no_file=False):
    """
    Run the different part of the program to directly obtain 
    """
    articulos = get_papers(author, max_papers=max_papers)
    if articulos is not None and len(articulos) != 0:
        citas = get_citations(articulos)
        if not no_screen:
            print_results(author, articulos, citas)
        if not no_file:
            filename = 'refs_{}.tex'.format(clean_author(author))
            print('Writing the LaTex file {}'.format(filename))
            print_results(author, articulos, citas, filename=filename)
            print('Done')
    else:
        print('No papers found, something went wrong. Check ADS token and Internet connection.')
        
"""
# The following is used if you want to have access to the intermediate results. Otherwise, use the command-line way.
import ads
import SNI_ads
ads.config.token = "5KAUJBW123456789dHCzvJWn73WyKVvNvyugC87M" # this one is fake, you need to use your own token
author = 'Morisset, C.'             
articulos = SNI_ads.get_papers(author)
citas = SNI_ads.get_citations(articulos)
SNI_ads.print_results(author, articulos, citas)
f = open('refs_{}.tex'.format(SNI_ads.clean_author(author)), 'w')
SNI_ads.print_results(author, articulos, citas, f)
f.close()
"""

if __name__ == '__main__':            
    parser = argparse.ArgumentParser()
    parser.add_argument("author", help="Author to search for.")
    parser.add_argument("-t", "--token", help="ADS token. Unused if the environment variable ADS_DEV_KEY is defined.")
    parser.add_argument("-m", "--max_papers", help="Maximum number of papers to consider.", type=int)
    parser.add_argument("-ns", "--no_screen", help="No screen output.", action="store_true")
    parser.add_argument("-nf", "--no_file", help="No file output.", action="store_true")
    parser.add_argument("-V", "--version", action="version", version=__version__,
                        help="Display version information and exit.")
    args = parser.parse_args()
    author = args.author
    if args.token is not None:
        ads.config.token = args.token
    do_all(author, max_papers=args.max_papers, no_screen=args.no_screen, no_file=args.no_file)
    
    
    
