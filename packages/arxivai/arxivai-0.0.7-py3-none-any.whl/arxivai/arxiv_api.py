import re

import requests
from bs4 import BeautifulSoup, SoupStrainer

regx = re.compile(r'(?<=/)\d+\.?\w+')
"""Extract arXiv paper id from url. ex) http://arxiv.org/abs/2001.04189v3 -> 2001.04189v3"""

def search(q, prefix='all', start=0, max_results=100, sort_by='relevance', sort_order='descending'):
    """Query the arXiv API.
    https://info.arxiv.org/help/api/user-manual.html#_query_interface

    Parameters
    ----------
    prefix	explanation
        ti	Title
        au	Author
        abs	Abstract
        co	Comment
        jr	Journal Reference
        cat	Subject Category
        rn	Report Number
        id	Id (use id_list instead)
        all	All of the above

    start   The index of the first result to return. Defaults to 0.        
    max_results Because of speed limitations in our implementation of the API, the maximum number of results returned from 
    a single call (max_results) is limited to 30000 in slices of at most 2000 at a time, using the max_results and start query parameters.
    For example to retrieve matches 6001-8000: http://export.arxiv.org/api/query?search_query=all:electron&start=6000&max_results=8000

    sortBy  relevance, lastUpdatedDate, submittedDate
    sortOrder   ascending, descending

    
    Returns
    -------
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <link href="http://arxiv.org/api/query?search_query%3D%26id_list%3D2303.08774%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
        <title type="html">ArXiv Query: search_query=&amp;id_list=2303.08774&amp;start=0&amp;max_results=10</title>
        <id>http://arxiv.org/api/QzNYWqKq+J4WS62/AKiDfpkbQx0</id>
        <updated>2023-05-16T00:00:00-04:00</updated>
        <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">1</opensearch:totalResults>
        <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
        <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:itemsPerPage>
        <entry>
            <id>http://arxiv.org/abs/2303.08774v3</id>
            <updated>2023-03-27T17:46:54Z</updated>
            <published>2023-03-15T17:15:04Z</published>
            <title>GPT-4 Technical Report</title>
            <summary>  We report the development of GPT-4, a large-scale, multimodal model which can ...</summary>
            <author>
                <name> OpenAI</name>
            </author>
            <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">100 pages</arxiv:comment>
            <link href="http://arxiv.org/abs/2303.08774v3" rel="alternate" type="text/html"/>
            <link title="pdf" href="http://arxiv.org/pdf/2303.08774v3" rel="related" type="application/pdf"/>
        </entry>
    </feed>
    """
    url = f'http://export.arxiv.org/api/query?search_query={prefix}:{q}&start={start}&max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml', parse_only=SoupStrainer('entry'))
    entries = list(soup)

    results = []
    for entry in entries:
        result = {
            'paper_id': re.findall(regx, entry.id.text)[0],
            'title': entry.find('title').text.replace('\n', ' ').strip(),
            'authors': [author.find('name').text.strip() for author in entry.find_all('author')],
            'category': entry.find('category')['term'],
            'abstract': entry.find('summary').text.replace('\n', ' ').strip(),
            'published': entry.find('published').text.split('T')[0],
        }
        results.append(result)

    return results



def fetch(arxiv_id):
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml', parse_only=SoupStrainer('entry'))

    result = {
        'paper_id': re.findall(regx, soup.id.text)[0],
        'title': soup.title.text.replace('\n', ' ').strip(),
        'authors': [author.find('name').text.strip() for author in soup.find_all('author')],
        'category': soup.find('category')['term'],
        'abstract': soup.summary.text.replace('\n', ' ').strip(),
        'published': soup.published.text.split('T')[0],
    }

    return result
