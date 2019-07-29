#!/usr/bin/env python3

import urllib.request
import html2text
import re
import PyRSS2Gen
import datetime
import yaml

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

if __name__ == "__main__":
    from pathlib import Path
    import os

    home = Path.home()

    with open(home / '.url-checker.yaml', 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    cache_path = home / ".cache" / "url-checker"
    if not os.path.exists(cache_path):
       os.makedirs(cache_path)

    updated_urls = []
    for url in config['urls']:
        contents = html2text.html2text(str(urllib.request.urlopen(url).read()))

        try:
            with open(cache_path / "{}.txt".format(slugify(url)), "r") as f:
                old_contents = f.read()
                f.close()
        except FileNotFoundError:
            old_contents = ""

        if (old_contents != contents):
            with open(cache_path / "{}.txt".format(slugify(url)), "w") as f:
                #f.seek(0)
                f.write(contents)
                #f.truncate()

                #print("url {} changed".format(url))
                updated_urls.append(url)

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
       
