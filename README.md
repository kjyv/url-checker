# url-checker
Simple script to check for modifications of URLs and output RSS of updated urls.

needs python3, python3-html2text, python3-PyRSS2Gen, python3-yaml

Intended to run as CGI script and can be called from RSS reader.

Set URLs to monitor in ~/.url-checker.yaml
Cached URL content is saved to ~/.cache/url-checker/
