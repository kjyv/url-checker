# url-checker
Simple script to check for modifications of specified URLs. If some are different, it
outputs a new RSS entry with updated urls (no history).
It is intended to run as a CGI script which can then be polled from your RSS reader.

Needs python3 and the following modules:
html2text, PyRSS2Gen, pyyaml, diff-match-patch, lxml, cssselect
(e.g. `apt install python3-html2text python3-pyrss2gen python3-yaml python3-diff-match-patch python3-lxml python3-cssselect`)

Create a file at ~/.url-checker.yaml with a list of URLs to be checked for differences like this:
```
urls:
        - ['https://domain.tld/updates.json', '', "https://domain.tld/releases"]
        - ['https://domain2.tld', '', '']
```
The second parameter on each line is an optional css selector to select a subset of the page for monitoring.
The third parameter is an optional alternative link to put into the output feed instead of the first url.

Cached URL content is saved to ~/.cache/url-checker/
