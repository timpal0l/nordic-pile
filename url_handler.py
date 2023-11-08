# This code is an adapted version of:
#  https://github.com/NVIDIA/Megatron-LM/blob/main/tools/openwebtext/blacklist_urls.py

import glob
import re
import tldextract

url_regex = None
BLACKLIST_DIR_PATH = "blacklisted_urls"

extension_blacklist = set()
domain_blacklist = set()
full_url_blacklist = set()


# Domains are one word only, not e.g. sv.wikipedia
# Extensions are a dot followed by one word
# Full urls can be anything, and blacklists all subdirectories of the given path/url e.g.:
# https://regeringen.se/myndigheter-med-flera/
# Would remove this:
# https://regeringen.se/myndigheter-med-flera/statens-namnd-for-arbetstagares-uppfinningar2/
def get_all_lines_in_subdir(subdir_name):

    files = [f for f in glob.glob(BLACKLIST_DIR_PATH + "/" + subdir_name + '/*.txt')]

    line_set = set()
    for file in files:
        with open(file, 'r') as f:
            new_set = [line.strip().lower() for line in f.readlines() if len(line.strip()) > 0]
            if subdir_name == "full_urls":
                new_set = [url.replace("https://", "").replace("http://", "") for url in new_set]
            line_set |= set(new_set)

    return line_set


def init():
    global url_regex, extension_blacklist, domain_blacklist, full_url_blacklist

    # Malformed urls. This function is adapted from:
    #  https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    url_regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    domain_blacklist = get_all_lines_in_subdir("domains")
    extension_blacklist = get_all_lines_in_subdir("extensions")
    full_url_blacklist = get_all_lines_in_subdir("full_urls")


def domain_is_in_blacklist(url):
    domain = tldextract.extract(url).domain

    return domain in domain_blacklist


def extension_is_in_blacklist(url):
    # if url.split('?')[0].split('.')[-1].endswith(extension_blacklist):
    if "." + url.split('?')[0].split('.')[-1] in extension_blacklist:
        return True
    return False


def url_is_malformed(url):
    return re.match(url_regex, url) is None


def full_url_is_in_blacklist(url):
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    if url in full_url_blacklist:
        return True
    for blacklisted_url in full_url_blacklist:
        if url.startswith(blacklisted_url):
            return True

    return False


def url_is_accepted(url):
    url = url.lower()
    if url_is_malformed(url):
        # print("Malformed url:", url)
        return False
    if domain_is_in_blacklist(url):
        # print("Domain blacklisted:", url)
        return False
    if extension_is_in_blacklist(url):
        # print("Extension blacklisted:", url)
        return False
    if len(url) <= 8:
        # print("Too short url:", url)
        return False
    if full_url_is_in_blacklist(url):
        # print("Full url is in blacklist:", url)
        return False

    return True


if __name__ == '__main__':
    init()
    urls = ["https://asd.com/hej", "asd.com/hej", "https://uhr.se", "https://sv.wikipedia.org/",
            "https://regeringen.se/myndigheter-med-flera/statens-namnd-for-arbetstagares-uppfinningar2/"]
    for url in urls:
        print("*" * 50)
        print("url:", url)
        print(url_is_accepted(url))
