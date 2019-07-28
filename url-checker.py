#!/opt/local/bin/python3.6

import urllib.request
import re
import PyRSS2Gen
import datetime

urls = (
        'https://zim-wiki.org/downloads/',
        )

def slugify(value):
    """
    (from Django)
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

if __name__ == "__main__":
    from pathlib import Path
    home = Path.home()
    cache_path = home / ".cache" / "url-checker"

    updated_urls = []
    for url in urls:
        contents = str(urllib.request.urlopen(url).read())

        with open(cache_path / "{}.txt".format(slugify(url)), "a+") as f:
            f.seek(0)
            old_contents = f.read()
            if (old_contents != contents):
                f.seek(0)
                f.write(contents)
                f.truncate()

                print("url {} changed".format(url))
                updated_urls.append(url)
            f.close()

    for url in updated_urls:
        updated_html = "<ul>"
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

        rss.write_xml(open("url-checker-feed.xml", "w"))

