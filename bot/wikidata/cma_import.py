#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Bot to import paintings from the Cleveland Museum of Art to Wikidata.

Use the CMA api to do the import


"""
import artdatabot
import pywikibot
import requests
import re
import time
import json
try:
    from html.parser import HTMLParser
except ImportError:
    import HTMLParser

def getCMAGenerator():
    """
    Generator to return Cleveland Museum of Art paintings
    """
    basesearchurl = u'http://openaccess-api.clevelandart.org/api/artworks/?type=Painting&skip=%s&limit=1000'

    htmlparser = HTMLParser()

    i = 0

    for i in range(0, 5000, 1000):
        searchurl = basesearchurl % (i, )

        searchpage = requests.get(searchurl)

        #print(json.dumps(searchpage.json(), indent=4, sort_keys=True))

        for iteminfo in searchpage.json().get("data"): #.get("search").get("results"):
            metadata = {}

            url = iteminfo.get('url').replace(u'http:', u'https:')
            print (url)

            metadata['url'] = url
            metadata['collectionqid'] = u'Q657415'
            metadata['collectionshort'] = u'CMA'
            metadata['locationqid'] = u'Q657415'

            #No need to check, I'm actually searching for paintings.
            metadata['instanceofqid'] = u'Q3305213'

            if not iteminfo.get('accession_number'):
                # We have one with None
                continue

            metadata['idpid'] = u'P217'
            metadata['id'] = iteminfo.get('accession_number')
            print (u'http://openaccess-api.clevelandart.org/api/artworks/%s' % (iteminfo.get('accession_number'),))

            title = iteminfo.get('title').replace('\n', ' ').replace('\r', ' ').strip(' ')
            # Chop chop, several very long titles
            if len(title) > 220:
                title = title[0:200].strip(' ')

            metadata['title'] = { u'en' : title,
                                  }

            nameregex = u'^(.+)\s\([^\)]+\)$'
            if (len(iteminfo.get('creators'))==0) or (len(iteminfo.get('creators'))==1) and not iteminfo.get('creators')[0].get('description'):
                metadata['description'] = { u'nl' : u'schilderij van anonieme schilder',
                                            u'en' : u'painting by anonymous painter',
                                            }
                metadata['creatorqid'] = "Q4233718"
            elif len(iteminfo.get('creators'))==1:
                namematch = re.match(nameregex, iteminfo.get('creators')[0].get('description'))
                if namematch:
                    name = namematch.group(1)
                else:
                    name = iteminfo.get('creators')[0].get('description')
                metadata['creatorname'] = name
                if iteminfo.get('creators')[0].get('qualifier'):
                    qualifier = iteminfo.get('creators')[0].get('qualifier').get('Value')
                    metadata['description'] = { u'en' : u'painting %s %s' % (qualifier, name, ),
                            }
                else:
                    metadata['description'] = { u'nl' : u'schilderij van %s' % (name, ),
                                                u'en' : u'painting by %s' % (name, ),
                                                u'de' : u'Gemälde von %s' % (name, ),
                                                u'fr' : u'peinture de %s' % (name, ),
                                                }
            else:
                name0match = re.match(nameregex, iteminfo.get('creators')[0].get('description'))
                if name0match:
                    name0 = name0match.group(1)
                else:
                    name0 = iteminfo.get('creators')[0].get('description')

                name1match = re.match(nameregex, iteminfo.get('creators')[1].get('description'))
                if name1match:
                    name1 = name1match.group(1)
                else:
                    name1 = iteminfo.get('creators')[1].get('description')

                if iteminfo.get('creators')[0].get('qualifier'):
                    qualifier0 = iteminfo.get('creators')[0].get('qualifier').get('Value')
                    description = u'painting %s %s and %s' % (qualifier0, name0, name1,)
                description = u'painting by %s and %s' % (name0, name1, )
                metadata['description'] = { u'en' : description,
                                            }

            if iteminfo.get('creation_date'):
                datecircaregex = u'^c\. (\d\d\d\d)$'
                datecircamatch = re.match(datecircaregex, iteminfo.get('creation_date'))
                if datecircamatch:
                    metadata['inception'] = datecircamatch.group(1).strip()
                    metadata['inceptioncirca'] = True
                elif iteminfo.get('creation_date_earliest') and iteminfo.get('creation_date_latest'):
                    if iteminfo.get('creation_date')==str(iteminfo.get('creation_date_earliest')) and \
                                iteminfo.get('creation_date')==str(iteminfo.get('creation_date_latest')):
                        metadata['inception'] = iteminfo.get('creation_date')
                    else:
                        metadata['inceptionstart'] = iteminfo.get('creation_date_earliest')
                        metadata['inceptionend'] = iteminfo.get('creation_date_latest')

            # Doesn't seem to be available (could strip from inventory number)
            # metadata['acquisitiondate'] = acquisitiondatematch.group(1)
            # Data is available, but too many different forms
            #if iteminfo.get('provenance'):

            if iteminfo.get('technique') and iteminfo.get('technique')==u'oil on canvas':
                metadata['medium'] = u'oil on canvas'

            if iteminfo.get('dimensions') and iteminfo.get('dimensions').get('unframed'):
                dimensions = iteminfo.get('dimensions').get('unframed')
                if dimensions.get('height') and dimensions.get('width'):
                    metadata['heightcm'] = u'%s' % (dimensions.get('height')*100,)
                    metadata['widthcm'] = u'%s' % (dimensions.get('width')*100,)
                    if dimensions.get('depth'):
                        metadata['depthcm'] = u'%s' % (dimensions.get('depth')*100,)

            # Image is available and they mark it with a license!
            if iteminfo.get('share_license_status') and iteminfo.get('share_license_status')==u'CC0':
                if iteminfo.get('images') and iteminfo.get('images').get('full'):
                    if iteminfo.get('images').get('full').get('url').endswith('.tif'):
                        metadata[u'imageurl'] = iteminfo.get('images').get('full').get('url')
                        metadata[u'imageurlformat'] = u'Q215106' # TIFF
                        metadata[u'imageurllicense'] = u'Q6938433' # CC0
                        metadata[u'imageurlforce'] = False # Already did a full forced run
            # No IIIF

            yield metadata

def main():
    dictGen = getCMAGenerator()

    #for painting in dictGen:
    #    print (painting)

    artDataBot = artdatabot.ArtDataBot(dictGen, create=True)
    artDataBot.run()

if __name__ == "__main__":
    main()
