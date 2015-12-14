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
   
class SNI(object):
    
    def __init__(self, author):

        self.author = author
        self.papers = None
        self.citations = {}
        
    def get_papers(self):
        
        res = ads.SearchQuery(author=self.author)
        try:
            self.papers = list(res)
            print('Got {} papers for {}'.format(len(self.papers), self.author))
        except:
            print('No papers')

    def get_citations(self):
        
        if self.papers is not None:
            for p in self.papers:
                N_citations = p.citation_count
                if N_citations > 0:
                    self.citations[p.bibcode] = []
                    for citation in p.citation:
                        self.citations[p.bibcode].append(ads.SearchQuery(bibcode=citation).next())
                    print('Got {} citations for paper {}.'.format(N_citations, p.bibcode))
    
def print_results(SNI, filename=None):
    
    if filename is None:
        def myprint(str):
            print(str)
    else:
        f = open(filename)
        def myprint(str):        
            f.write(str + '\n')

    
    for p in sorted(SNI.papers , key=lambda pp: pp.year):
        typeA = [] # no autocitas
        typeB = [] # autocitas por coauthor
        typeC = [] # autocita
        N_citations = p.citation_count
        authors = [pretty_author_name(a) for a in p.author]
        if N_citations > 0:
            for citing in SNI.citations[p.bibcode]:
                autocite = False
                autociteco = False
                for author in citing.author:
                    if pretty_author_name(author) == pretty_author_name(SNI.author):
                        autocite = True
                    elif pretty_author_name(author) in authors:
                        autociteco = True
                if autocite:
                    typeC.append(citing)
                elif autociteco:
                    typeB.append(citing)
                else:
                    typeA.append(citing)
            myprint('{} {}, {}, {}, {}: Total = {}, Type A = {}, type B = {}, type C = {}'.format(auts(p), cv(p.year), cv(p.pub), cv(p.volume), cv(p.page[0]), 
                                                                                                p.citation_count,
                                                                                len(typeA), len(typeB), len(typeC)))
            if len(typeA) > 0:
                myprint('{\\bf Citations Type A:}')
                myprint('\\begin{itemize}')
                for pc in typeA:
                    myprint('\item {} {}, {}, {}, {}'.format(auts(pc), cv(pc.year), cv(pc.pub), cv(pc.volume), cv(pc.page[0])))
                myprint('\end{itemize}')
            if len(typeB) > 0:
                myprint('{\\bf Citations Type B:}')
                myprint('\\begin{itemize}')
                for pc in typeB:
                    myprint('\item {} {}, {}, {}, {}'.format(auts(pc), cv(pc.year), cv(pc.pub), cv(pc.volume), cv(pc.page[0])))
                myprint('\end{itemize}')
            myprint('\\hline')
            myprint('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                
    if filename is not None:
        f.close()       



"""                    
S = SNI('Morisset, C.')
S.get_papers()
S.get_citations()
S.print_results()
"""