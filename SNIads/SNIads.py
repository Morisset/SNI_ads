#!/usr/bin/env python
'''
Created on 14 dec. 2015

@author: christophemorisset

'''


#from __future__ import unicode_literals
import sys
import ads
import requests.packages.urllib3
from unidecode import unidecode
import argparse
from distutils.version import LooseVersion
from .version import version

if LooseVersion(ads.__version__) < LooseVersion('0.11.3'):
    raise Exception('ads version is {}. You must update ads to at least v0.11.3 to use this version of SNI_ads. Use "pip install -U ads"'.format(ads.__version__))

requests.packages.urllib3.disable_warnings()
MAX_pages = 1000
MAX_papers = 1000000

#cv = lambda str: unicode(str).encode('utf8')
#cv = lambda str: unidecode(str).replace('$', '').replace('#', '').replace('&', '').replace('_', '\_')    
if sys.version_info.major < 3:
    cv = lambda str: unidecode(str).translate(None, '$#&').replace('_', '\_')    
    def isFile(f):
        return isinstance(f, file) 
else:
    table = str.maketrans(dict.fromkeys('$#&'))
    cv = lambda str: unidecode(str).translate(table).replace('_', '\_')    
    def isFile(f):
        return hasattr(f, 'read') 


clean_author = lambda author: ''.join([s for s in author if s not in ('.', ' ', ',')])

def read_bibcode_file(filename):
    
    res = []
    with open(filename, 'r') as datafile:
        for row in datafile:
            if row[0] != "#" and row[0] != "\n":
                if sys.version_info.major < 3:
                    res.append(row.strip().translate(None, '[](){}'))
                else:
                    table = str.maketrans(dict.fromkeys('[](){}'))
                    res.append(row.strip().translate(table))
    return res
    

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
        return cv(authors)

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
         
def clean_arXiv(papers):
    """
    Take a list of papers and return the same list without the arXiv doblets
    """
    res = []
    for p in papers:
        keep_it = True
        if p.pub == 'ArXiv e-prints':
            for p2 in papers:
                #if auts(p) == auts(p2) and p2.pub != 'ArXiv e-prints':
                #    print('!!!!!!-1-  {} '.format(cv(p.title[0])))
                #    print('!!!!!!-2-  {} '.format(cv(p2.title[0])))
                if cv(p.title[0]) == cv(p2.title[0]) and auts(p) == auts(p2) and p2.pub != 'ArXiv e-prints':
                    keep_it = False
                    print('Removing {}'.format(p.title)) 
        if keep_it:
            res.append(p)
    return res    

def get_papers(author, max_papers=None, token=None, ex_file=None, in_file=None, verbose=False):
    """
    Returns a list of all the papers from author that contain at least one citation.
    max_paper can reduce the number of papers. The default is MAX_papers (1000000)
    author is a string.
    The papers are ads.search.Article
    """
    if max_papers is None:
        max_papers = MAX_papers
    if in_file is not None:
        in_bibcodes = read_bibcode_file(in_file)
        papers = []
        for bibcode in in_bibcodes[0:max_papers]:
            if verbose:
                print('get_papers for bibcode = {}'.format(bibcode))
            res =  ads.SearchQuery(bibcode=bibcode, 
                                   fl='author, title, year, pub, volume, page, citation, citation_count, bibcode',
                                   max_pages=MAX_pages,
                                   token=token)
            
            papers.extend(list(res))
    else:
        res = ads.SearchQuery(author=author, 
                          fl='author, title, year, pub, volume, page, citation, citation_count, bibcode',
                          max_pages=MAX_pages,
                          token=token)
        try:
            papers = list(res)
        except:
            papers = None
    try:
        papers = [p for p in papers if p.citation_count > 0][0:max_papers]
    except:
        papers = None
        print('Got 0 papers from {} with at least one citation'.format(author))
        return papers
    if ex_file is not None:
        ex_bibcodes = read_bibcode_file(ex_file)
        papers = [p for p in papers if p.bibcode not in ex_bibcodes]
    print('Got {} papers from {} with at least one citation'.format(len(papers), author))
    return papers

def get_citations(papers, token=None, verbose=False):
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
                if verbose:
                    print('get_citations for paper {}'.format(p.title))
                res = ads.SearchQuery(q='citations(bibcode:{})'.format(p.bibcode), 
                                      fl='author, title, year, pub, volume, page, bibcode',
                                      max_pages=MAX_pages,
                                      token=token)
                citations[p.bibcode] = clean_arXiv(list(res))
                print('Got {} citations for paper {}.'.format(N_citations, p.bibcode))
    return citations

def print_results(author, papers, citations, filename=None, verbose=False):
    """
    Print the results on the screen and in a file.
    """
    if filename is None:
        def myprint(str):
            print(str)
    elif isFile(filename):
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
    total_typeA = 0
    total_typeB = 0
    total_typeC = 0
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
                try:
                    for this_author in citing.author:
                        if verbose:
                            print('print_results for paper {} and coauthor {}'.format(p.title, this_author))
                        if pretty_author_name(this_author) == pretty_author_name(author):
                            autocite = True
                        elif pretty_author_name(this_author) in [cv(a) for a in authors]:
                            autociteco = True
                    if autocite:
                        typeC.append(citing)
                    elif autociteco:
                        typeB.append(citing)
                    else:
                        typeA.append(citing)
                except:
                    pass
            total_typeA += len(typeA)
            total_typeB += len(typeB)
            total_typeC += len(typeC)
            this_count = len(typeA) + len(typeB) + len(typeC)
            if len(typeA) + len(typeB) > 0:
                myprint('\\item {} \\\ '.format(pretty_ref(p, with_title=True)))
                myprint('Total = {}, Type A = {}, type B = {}, type C = {} \\\ '.format(this_count,
                                                                                        len(typeA), 
                                                                                        len(typeB), 
                                                                                        len(typeC)))
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
    totall= total_typeA, +total_typeB + total_typeC
    myprint('TOTAL {} type A = {}, type B = {}, type C = {}'.format(totall, total_typeA, total_typeB, total_typeC))
    myprint('\\end{document}')
    if filename is not None and not isFile(filename):
        f.close()

def do_all(author, max_papers=None, no_screen=False, no_file=False, 
           token=None, ex_file=None, in_file=None, verbose=None):
    """
    Run the different part of the program to directly obtain the LaTex file
    """
    articulos = get_papers(author, max_papers=max_papers, 
                           token=token, ex_file=ex_file, in_file=in_file, verbose=verbose)
    if verbose:
        print('Python version: ', sys.version_info.major)
        
    if articulos is not None and len(articulos) != 0:
        citas = get_citations(articulos, token=token, verbose=verbose)
        if not no_screen:
            print_results(author, articulos, citas, verbose=verbose)
        if not no_file:
            filename = 'refs_{}.tex'.format(clean_author(author))
            print('Writing the LaTex file {}'.format(filename))
            print_results(author, articulos, citas, filename=filename, verbose=verbose)
            print('Done')
    else:
        print('No papers found, something went wrong. Check ADS token and Internet connection.')
        
"""
# The following is used if you want to have access to the intermediate results. Otherwise, use the command-line way.
from SNIads import SNIads
token = "5KAUJBW123456789dHCzvJWn73WyKVvNvyugC87M" # this one is fake, you need to use your own token
# token=None # use this is you defined the token using the ADS_DEV_KEY environment variable
author = 'Morisset, C.'             
articulos = SNIads.get_papers(author, token=token)
citas = SNIads.get_citations(articulos, token=token)
SNIads.print_results(author, articulos, citas)
f = open('refs_{}.tex'.format(SNIads.clean_author(author)), 'w')
SNIads.print_results(author, articulos, citas, f)
f.close()
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("author", help="Author to search for.", default='')
    parser.add_argument("-t", "--token", help="ADS token. It can also be stored in ADS_DEV_KEY environment variable.")
    parser.add_argument("-m", "--max_papers", help="Maximum number of papers to consider.", type=int)
    parser.add_argument("-ns", "--no_screen", help="No screen output.", action="store_true")
    parser.add_argument("-nf", "--no_file", help="No file output.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose", action="store_true")
    parser.add_argument("-V", "--version", action="version", version=version,
                        help="Display version information and exit.")
    parser.add_argument("-ex", "--exclude_bibcodes", help="A filename containing the bibcodes to be excluded")
    parser.add_argument("-in", "--include_bibcodes", help="A filename containing the bibcodes to be included. In this case, the author may be omitted")
    args = parser.parse_args()
    if args.author == '' and args.include_bibcodes is None:
        raise ValueError('at least an author name or an include file must be given')
    do_all(args.author, max_papers=args.max_papers, no_screen=args.no_screen, no_file=args.no_file, 
           token=args.token, ex_file = args.exclude_bibcodes, in_file=args.include_bibcodes, verbose=args.verbose)

if __name__ == '__main__':            
    main()
    
    
