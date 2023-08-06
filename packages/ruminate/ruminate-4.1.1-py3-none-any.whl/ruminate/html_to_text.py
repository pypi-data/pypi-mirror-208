from bs4 import BeautifulSoup


def html_to_text(html):
    soup = BeautifulSoup(html, "html5lib")
    result = soup.get_text(" ", strip=True) # noqa
    return result
