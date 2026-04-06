#!/usr/bin/env python
'''
Created on 14 dec. 2015

@author: christophemorisset

'''


import ads
import requests.packages.urllib3
from unidecode import unidecode
import argparse
from packaging.version import Version
try:
    import tomllib as _tomllib
except ImportError:
    try:
        import tomli as _tomllib
    except ImportError:
        _tomllib = None

def _read_version():
    if _tomllib is not None:
        import os
        _pyproject = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyproject.toml')
        try:
            with open(_pyproject, 'rb') as _f:
                return _tomllib.load(_f)['project']['version']
        except Exception:
            pass
    from importlib.metadata import version as _get_version, PackageNotFoundError as _PNF
    try:
        return _get_version("SNIads")
    except _PNF:
        return "unknown"

_version = _read_version()

if Version(ads.__version__) < Version('0.11.3'):
    raise Exception(f'ads version is {ads.__version__}. You must update ads to at least v0.11.3 to use this version of SNI_ads. Use "pip install -U ads"')

requests.packages.urllib3.disable_warnings()
MAX_pages = 1000
MAX_papers = 1000000

_latex_table = str.maketrans(dict.fromkeys('$#&'))

def cv(s):
    if type(s) == str:
        return unidecode(s).translate(_latex_table).replace('_', r'\_')
    elif type(s) == list:
        return ' ; '.join(cv(ss) for ss in s)
    else:
        return s

def isFile(f):
    return hasattr(f, 'read')

def clean_author(author):
    return ''.join(s for s in author if s not in ('.', ' ', ','))

def read_bibcode_file(filename):
    
    _table = str.maketrans(dict.fromkeys('[](){}'))
    res = []
    with open(filename, 'r') as datafile:
        for row in datafile:
            if row[0] != "#" and row[0] != "\n":
                res.append(row.strip().translate(_table))
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
        return f"{cv(res1)}, {cv(res2)}."
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
    r"""
    Returns a string in the form
    authors, year, {\it title}, pub, volume, page
    by default, title is not included. Changed by with_title keyword.
    type(p) is ads.search.Article
    """
    try:
        year = f', {cv(p.year)}'
    except (AttributeError, TypeError):
        year = ''
    try:
        pub = f', {cv(p.pub)}'
    except (AttributeError, TypeError):
        pub = ''
    try:
        volume = f', {cv(p.volume)}'
    except (AttributeError, TypeError):
        volume = ''
    try:
        page = f', {cv(p.page[0])}'
    except (AttributeError, TypeError, IndexError):
        page = ''
    if with_title:
        try:
            title = f', {{\\it {cv(p.title[0])}}}'
        except (AttributeError, TypeError, IndexError):
            title = ''
    else:
        title = ''
        
    return f'{auts(p)}{year}{title}{pub}{volume}{page}'
         
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
                    print(f'Removing {p.title}')
        if keep_it:
            res.append(p)
    return res    

def get_papers(author, max_papers=None, token=None, ex_file=None, in_file=None, verbose=False, rows=200, only_cited=False, start_year=None):
    """
    Returns a list of all the papers from author that contain at least one citation.
    max_paper can reduce the number of papers. The default is MAX_papers (1000000)
    author is a string.
    The papers are ads.search.Article
    rows controls the number of results per page (default 200); higher values reduce pagination errors.
    """
    if max_papers is None:
        max_papers = MAX_papers
    if in_file is not None:
        in_bibcodes = read_bibcode_file(in_file)
        papers = []
        for bibcode in in_bibcodes[0:max_papers]:
            if verbose:
                print(f'get_papers for bibcode = {bibcode}')
            res = ads.SearchQuery(bibcode=bibcode,
                                  fl='author, title, year, pub, volume, page, citation, citation_count, bibcode',
                                  rows=rows,
                                  max_pages=MAX_pages,
                                  token=token)
            try:
                papers.extend(list(res))
            except Exception as e:
                print(f'Error querying ADS for bibcode {bibcode}: {e}')
    else:
        res = ads.SearchQuery(author=author,
                              fl='author, title, year, pub, volume, page, citation, citation_count, bibcode',
                              rows=rows,
                              max_pages=MAX_pages,
                              token=token)
        try:
            papers = list(res)
        except Exception as e:
            print(f'Error querying ADS for author {author}: {e}')
            papers = None
    try:
        if only_cited:
             papers = [p for p in papers if p.citation_count > 0][0:max_papers]
        else:
            papers = [p for p in papers][0:max_papers]
        if start_year is not None:
            papers = [p for p in papers if int(p.year) >= start_year]
    except (TypeError, AttributeError):
        papers = None
        print(f'Got 0 papers from {author} with at least one citation')
        return papers
    if ex_file is not None:
        ex_bibcodes = read_bibcode_file(ex_file)
        papers = [p for p in papers if p.bibcode not in ex_bibcodes]
    print(f'Got {len(papers)} papers from {author}')
    return papers

def get_citations(papers, token=None, verbose=False, rows=200):
    """
    papers: list of ads.search.Article
    Returns a dictionnary where each key corresponds to the bibcode of one element of papers and the value is a list of
    papers citing the given paper.
    rows controls the number of results per page (default 200); higher values reduce pagination errors.
    """
    citations = {}
    if papers is not None:
        for p in sorted(papers , key=lambda pp: (pp.year, pp.author[0])):
            N_citations = p.citation_count
            if N_citations > 0:
                if verbose:
                    print(f'get_citations for paper {p.title}')
                res = ads.SearchQuery(q=f'citations(bibcode:{p.bibcode})',
                                      fl='author, title, year, pub, volume, page, bibcode',
                                      rows=rows,
                                      max_pages=MAX_pages,
                                      token=token)
                try:
                    citations[p.bibcode] = clean_arXiv(list(res))
                except Exception as e:
                    print(f'Error fetching citations for {p.bibcode}: {e}')
                    citations[p.bibcode] = []
                print(f'Got {N_citations} citations for paper {p.bibcode}.')
            else:
                print(f'No citations for paper {p.bibcode}.')
    return citations

def print_results(author, papers, citations, filename=None, verbose=False, only_cited=True):
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
            myprint(f'\\item {pretty_ref(p, with_title=True)} \\\\')
            myprint(f'ADS link: https://ui.adsabs.harvard.edu/abs/{p.bibcode.replace("&", r"\&")}/abstract \\\\')
            myprint(f'DOI: {cv(p.doi) if hasattr(p, "doi") else "N/A"} \\\\')
            for citing in citations[p.bibcode]:
                autocite = False
                autociteco = False
                try:
                    for this_author in citing.author:
                        if verbose:
                            print(f'print_results for paper {p.title} and coauthor {this_author}')
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
                except (AttributeError, TypeError):
                    pass
            total_typeA += len(typeA)
            total_typeB += len(typeB)
            total_typeC += len(typeC)
            this_count = len(typeA) + len(typeB) + len(typeC)
            if this_count > 0:
                myprint(f'Total = {this_count}, Type A = {len(typeA)}, type B = {len(typeB)}, type C = {len(typeC)} \\\\')
                if len(typeA) > 0:
                    myprint('{\\bf Citations Type A:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeA , key=lambda pp: (pp.year, pp.author[0])):
                        myprint(f'\\item {pretty_ref(pc)}')
                    myprint('\\end{itemize}')
                if len(typeB) > 0:
                    myprint('{\\bf Citations Type B:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeB , key=lambda pp: (pp.year, pp.author[0])):
                        myprint(f'\\item {pretty_ref(pc)}')
                    myprint('\\end{itemize}')
                if len(typeC) > 0:
                    myprint('{\\bf Citations Type C:}')
                    myprint('\\begin{itemize}')
                    for pc in sorted(typeC , key=lambda pp: (pp.year, pp.author[0])):
                        myprint(f'\\item {pretty_ref(pc)}')
                    myprint('\\end{itemize}')
        elif not only_cited:
            myprint(f'\\item {pretty_ref(p, with_title=True)} \\\\')
            myprint(f'ADS link: https://ui.adsabs.harvard.edu/abs/{p.bibcode.replace("&", r"\&")}/abstract \\\\')
            myprint(f'DOI: {cv(p.doi) if hasattr(p, "doi") else "N/A"} \\\\')
            myprint('No citations \\\\')
        myprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    myprint('\\end{enumerate}')
    totall = total_typeA + total_typeB + total_typeC
    myprint(f'TOTAL {totall} type A = {total_typeA}, type B = {total_typeB}, type C = {total_typeC}')
    myprint('\\end{document}')
    if filename is not None and not isFile(filename):
        f.close()

def do_all(author, max_papers=None, no_screen=False, no_file=False,
           token=None, ex_file=None, in_file=None, verbose=None, rows=200, only_cited=False, start_year=None):
    """
    Run the different part of the program to directly obtain the LaTex file
    """
    articulos = get_papers(author, max_papers=max_papers,
                           token=token, ex_file=ex_file, in_file=in_file, verbose=verbose, rows=rows, only_cited=only_cited, start_year=start_year)
    if articulos is not None and len(articulos) != 0:
        citas = get_citations(articulos, token=token, verbose=verbose, rows=rows)
        if not no_screen:
            print_results(author, articulos, citas, verbose=verbose, only_cited=only_cited)
        if not no_file:
            filename = f'refs_{clean_author(author)}.tex'
            print(f'Writing the LaTex file {filename}')
            print_results(author, articulos, citas, filename=filename, verbose=verbose, only_cited=only_cited)
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
    parser.add_argument("-oc", "--only_cited", help="Only cited papers are printed.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose", action="store_true")
    parser.add_argument("-V", "--version", action="version", version=_version,
                        help="Display version information and exit.")
    parser.add_argument("-ex", "--exclude_bibcodes", help="A filename containing the bibcodes to be excluded")
    parser.add_argument("-in", "--include_bibcodes", help="A filename containing the bibcodes to be included. In this case, the author may be omitted")
    parser.add_argument("-r", "--rows", help="Number of ADS results per page (default 200).", type=int, default=200)
    parser.add_argument("-sy", "--start_year", help="Only papers published from this year onwards are considered.", type=int)
    args = parser.parse_args()
    if args.author == '' and args.include_bibcodes is None:
        raise ValueError('at least an author name or an include file must be given')
    do_all(args.author, max_papers=args.max_papers, no_screen=args.no_screen, no_file=args.no_file,
           token=args.token, ex_file=args.exclude_bibcodes, in_file=args.include_bibcodes, verbose=args.verbose,
           rows=args.rows, only_cited=args.only_cited, start_year=args.start_year)

if __name__ == '__main__':            
    main()
    
    
