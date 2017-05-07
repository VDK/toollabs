#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Take the item https://www.wikidata.org/wiki/Q6009893
Loop over the connected categories using petscan to find painting candidates.

Publish the result as a table on:
 https://www.wikidata.org/wiki/Wikidata:WikiProject_sum_of_all_paintings/Possible_paintings
"""
import pywikibot
import requests

def wikidataCategoryGenerator(repo, qid, project):
    '''
    Generator that takes a category item
    '''
    categoryitem = pywikibot.ItemPage(repo, title=qid)
    for categorypage in categoryitem.iterlinks(family=project):
        gen = petscanGenerator(repo, categorypage.site.lang, u'wikipedia', 8, categorypage.title(withNamespace=False))
        for item in gen:
            yield item

def petscanGenerator(repo, lang, project, depth, categories):
    '''
    * Language
    * Project
    * Depth
    * Categories
    * Namespace
    * Pages with items
    * Has no statements
    '''
    query = u'https://petscan.wmflabs.org/?language=%(lang)s&project=%(project)s&depth=%(depth)s' \
            u'&categories=%(categories)s&combination=subset&ns%%5B0%%5D=1&show_redirects=no&edits%%5Bbots%%5D=both' \
            u'&edits%%5Banons%%5D=both&edits%%5Bflagged%%5D=both&subpage_filter=either&common_wiki=auto' \
            u'&wikidata_item=with&wpiu=any&wpiu_no_statements=1&cb_labels_yes_l=1&cb_labels_any_l=1&cb_labels_no_l=1' \
            u'&format=json&output_compatability=catscan&sortby=none&sortorder=ascending&min_redlink_count=1' \
            u'&doit=Do%%20it%%21&interface_language=en&active_tab=tab_output'
    url = query % { u'lang' : lang,
                    u'project' : project,
                    u'depth' : depth,
                    u'categories' : categories,}
    # Sometimes breaks, just skip it and it will return in the next run
    try:
        petpage = requests.get(url)
        for pageinfo in petpage.json().get(u'*')[0].get(u'a').get('*'):
            yield { u'title' : pageinfo.get(u'title').replace(u'_', u' '),
                    u'q' : pageinfo.get(u'q'),
                    u'lang' : lang,
                    }
    except ValueError:
        return


def main():
    repo = pywikibot.Site().data_repository()
    gen = wikidataCategoryGenerator(repo, u'Q6009893', u'wikipedia')
    text = u'{{/header}}\n\n'
    text = text + u'{| class="wikitable sortable"\n'
    text = text + u'! Item !! Language  !! Title\n|-'
    i = 0
    langstats = {}
    for iteminfo in gen:
        text = text + u'| [[%(q)s]] || %(lang)s || [[:%(lang)s:%(title)s|%(title)s]]\n|-\n' % iteminfo
        i = i + 1
        if iteminfo.get(u'lang') not in langstats:
            langstats[iteminfo.get(u'lang')]=1
        else:
            langstats[iteminfo.get(u'lang')] = langstats[iteminfo.get(u'lang')] + 1

    text = text + u'|}\n\nSome statistics:\n'
    text = text + u'{| class="wikitable sortable"\n'
    text = text + u'! Language code !! Language !! Count\n|-'
    for lang in sorted(langstats.keys()):
        text = text + u'| %s || {{#language:%s}} || %s \n|-\n' % (lang, lang, langstats.get(lang))
    text = text + u'|- class="sortbottom"\n'
    text = text + u'| || %s || %s\n' % (len(langstats.keys()), i)
    text = text + u'|}\n[[Category:WikiProject sum of all paintings|Possible paintings]]\n'
    pagetitle = u'Wikidata:WikiProject sum of all paintings/Possible paintings'
    page = pywikibot.Page(repo, title=pagetitle)
    summary = u'Found %s possible paintings' % (i,)
    page.put(text, summary)

if __name__ == "__main__":
    main()
