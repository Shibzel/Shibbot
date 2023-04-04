import re
from string import ascii_letters, digits
from urllib3.util.url import parse_url


ANSI_ESCAPE_REGEX = re.compile(r'\x1b[^m]*m')
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

def remove_chars(string: str, chars: str = "", replace: str = "") -> str:
    """Removes characters from string."""
    return re.sub(r"["+chars+"]", replace, string)

def remove_ansi_escape_sequences(string: str):
    return ANSI_ESCAPE_REGEX.sub(lambda match: (match.group()
                                    if match.group() == '\x1b[0m' 
                                    else ''), string)
    
def get_urls(string) -> list[str]:
    results = re.findall(URL_REGEX, string)
    for i, url in enumerate(results):
        url = re.sub(r"[^A-Za-z\.:\/]", "", url)
        while url[-1] not in ascii_letters+digits:
            url = url[:-1]
        results[i] = url
    return results

def url_to_domain(url: str) -> list[str]:
    domain = parse_url(url).netloc
    splited = domain.split(".")
    return [".".join(splited[i:]) for i in range(len(splited)-1)]


if __name__ == "__main__":
    import timeit

    to_time = """
string = "Links: https://cornhub.website/, http://cornhub.website, https://sus.amongousse.fun."
urls = get_urls(string)
for url in urls:
    domains = url_to_domain(url)
"""
        
    print(timeit.timeit(to_time, number=1000, globals=globals())) # 0.05154949999996461