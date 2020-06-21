#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A bot to normalize painting genres. See:
https://www.wikidata.org/wiki/Wikidata:WikiProject_sum_of_all_paintings/Genre#Normalization

"""
import pywikibot
from pywikibot import pagegenerators, WikidataBot

class PaintingGenreBot(WikidataBot):
    """
    A bot to normalize painting genre. Uses the WikidataBot for the basics.
    """
    def __init__(self):
        """
        No arguments, bot makes it's own generator based on the genres
        """
        super(PaintingGenreBot, self).__init__()
        self.use_from_page = False
        self.genres = { u'Q1400853' : u'Q134307', # portrait painting -> portrait
                        u'Q2414609' : u'Q2864737', # religious painting -> religious art
                        u'Q214127' : u'Q1047337', # genre painting -> genre art
                        u'Q107425' : u'Q191163', # landscape -> landscape art
                        u'Q333357' : u'Q128115', # abstract painting -> abstract art
                        u'Q18535' : u'Q2839016', # allegory (figure of speech) -> allegory (art genre)
                        u'Q11766730' : u'Q2839016', # allegorical painting (Q11766730) -> allegory (art genre)
                        u'Q11766734' : u'Q158607', # marine painting (Q11766734) -> marine art (Q158607)
                        u'Q3368492' : u'Q390001', # pastorale in painting (Q3368492) -> pastoral (Q390001)
                        u'Q2302151' : u'Q16875712', #  animal painting (Q2302151) ->  animal art (Q16875712)
                        }
        self.generator = self.getGenerator()

    def getGenerator(self):
        """
        Get a generator of paintings that have one of the replacable genres
        :return: A generator that yields ItemPages
        """
        query = u'SELECT ?item WHERE { ?item wdt:P31 wd:Q3305213 . ?item wdt:P136 ?genre  .VALUES ?genre {'

        for genre in list(self.genres.keys()):
            query = query + u' wd:%s ' % (genre,)
        query = query + u' }  }'

        generator = pagegenerators.PreloadingItemGenerator(pagegenerators.WikidataSPARQLPageGenerator(query,
                                                                                                      site=self.repo))
        return generator

    def treat_page_and_item(self, page, item):
        """Treat each item, page is probably None."""
        if not item.exists():
            return

        data = item.get()
        claims = data.get('claims')

        if not u'P136' in claims:
            return

        summary = u'[[Wikidata:WikiProject sum of all paintings/Genre#Normalization|Genre normalization for paintings]]'

        for claim in claims.get(u'P136'):
            currentgenre = claim.getTarget().title()
            if currentgenre in self.genres:
                newgenre = self.genres.get(currentgenre)
                genreItem = pywikibot.ItemPage(self.repo, title=newgenre)
                pywikibot.output(u'Replacing %s with %s' % (currentgenre, newgenre))
                claim.changeTarget(genreItem, summary=summary)


def main(*args):
    """
    """
    paintingBot = PaintingGenreBot()
    paintingBot.run()

if __name__ == "__main__":
    main()
