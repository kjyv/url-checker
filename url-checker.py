#!/usr/bin/env python3

import urllib.request
import html2text
import re
import PyRSS2Gen
import datetime
import yaml
#import Levenshtein
from diff_match_patch import diff_match_patch

from lxml import etree
from cssselect import GenericTranslator, SelectorError

def slugify(value):
    """
    (from Django)
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def compute_similarity_and_diff(text1, text2):
    dmp = diff_match_patch()
    dmp.Diff_Timeout = 0.0
    diff = dmp.diff_main(text1, text2, False)

    # similarity
    common_text = sum([len(txt) for op, txt in diff if op == 0])
    text_length = max(len(text1), len(text2))
    sim = common_text / text_length

    return sim, diff

if __name__ == "__main__":
    from pathlib import Path
    import os

    home = Path.home()

    with open(home / '.url-checker.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    cache_path = home / ".cache" / "url-checker"
    if not os.path.exists(cache_path):
       os.makedirs(cache_path)

    updated_urls = []
    for url, selector, link in config['urls']:
        #print("get {} ...".format(url), flush=True)
        html = str(urllib.request.urlopen(url).read())

        if selector != "":
            #css selector given, parse html and extract subtree
            parsed = etree.HTML(html)
            try:
                expression = GenericTranslator().css_to_xpath(selector)
            except SelectorError:
                print('Invalid selector.')

            contents = [etree.tostring(e, method="text", encoding='unicode') for e in parsed.xpath(expression)]
            if (len(contents) > 0):
                contents = contents[0]
            else:
                contents = "nothing selected"
        else:
            #no css selector given, simply convert html to text
            contents = html2text.html2text(html)

        #print("read cache for {} ...".format(url), flush=True)
        try:
            with open(cache_path / "{}.txt".format(slugify(url)), "r") as f:
                old_contents = f.read()
                f.close()
        except FileNotFoundError:
            old_contents = ""

        #print("compare with cache, similarity...", flush=True)
        #https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings/50102520#50102520
        #similarity = Levenshtein.ratio(old_contents, contents)

        #Levenshtein is too slow for larger websites
        similarity, diff = compute_similarity_and_diff(old_contents, contents)

        #print("url {} has similarity {} to previous version".format(url, str(similarity)), flush=True)

        if (similarity < 0.99):
            with open(cache_path / "{}.txt".format(slugify(url)), "w") as f:
                #f.seek(0)
                f.write(contents)
                #f.truncate()

                print("url {} changed (similarity is {})".format(url, similarity))
                url = link if link is not None and link != '' else url
                updated_urls.append(url)
        else:
            print("url {} is the same or very similar to previous version ({})".format(url, similarity))

    updated_html = ""
    for url in updated_urls:
        updated_html += "<ul>"
        updated_html += '<li><a href="{}">{}</a></li>'.format(url, url)
        updated_html += "</ul>"

    if len(updated_urls) > 0:
        rss = PyRSS2Gen.RSS2(
            title = "URL update notifications",
            link = "",
            description = "Show updates of predefined URLs",
            #lastBuildDate = datetime.datetime.now(),
            items = [PyRSS2Gen.RSSItem(
                title = "Updates on {}".format(datetime.datetime.now()),
                link = str(url),
                description = "{}".format(updated_html),
                pubDate = datetime.datetime.now()
            )]
        )

        rss.write_xml(open(cache_path / "url-checker-feed.xml", "w"))
        print("Content-Type: text/xml; charset=utf-8\n")
        print(rss.to_xml())
    else:
        #output previous rss file
        with open(cache_path / "url-checker-feed.xml", "r") as f:
            contents = f.read()
            print("Content-Type: text/xml; charset=utf-8\n")
            print(str(contents))
            f.close()

