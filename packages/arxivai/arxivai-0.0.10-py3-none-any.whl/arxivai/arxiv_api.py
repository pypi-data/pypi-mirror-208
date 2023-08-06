import re

import feedparser
import requests

regx_id = re.compile(r'(?<=/)\d+\.?\w+')
"""
    Extract arXiv paper id from url. ex) http://arxiv.org/abs/2001.04189v3 -> 2001.04189v3
    Query the arXiv API.
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
def search(q, prefix='all', start=0, max_results=100, sort_by='relevance', sort_order='descending'):
    url = f'http://export.arxiv.org/api/query?search_query={prefix}:{q}&start={start}&max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}'
    parser = feedparser.parse(requests.get(url).text)

    results = []
    for entry in parser['entries']:
        result = {
            'paper_id': entry['id'],
            'paper_id': re.search(regx_id, entry['id']).group(),
            'title': entry['title'],
            'authors': [author['name'] for author in entry['authors']],
            'categories': [tag['term'] for tag in entry['tags']],
            'abstract': entry['summary'].replace('\n', ' ').strip(),
            'published': entry['published'].split('T')[0],
        }
        results.append(result)

    return results



def fetch(arxiv_id):
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    parser = feedparser.parse(requests.get(url).text)

    entry = parser['entries'][0]
    result = {
        'paper_id': re.search(regx_id, entry['id']).group(),
        'title': entry['title'],
        'authors': [author['name'] for author in entry['authors']],
        'categories': [tag['term'] for tag in entry['tags']],
        'abstract': entry['summary'].replace('\n', ' ').strip(),
        'published': entry['published'].split('T')[0],
    }

    return result


def fetchall(arxiv_ids:list):
    id_list = ','.join(arxiv_ids)
    url = f'http://export.arxiv.org/api/query?id_list={id_list}'
    parser = feedparser.parse(requests.get(url).text)

    results = []
    for entry in parser['entries']:
        result = {
            'paper_id': re.search(regx_id, entry['id']).group(),
            'title': entry['title'],
            'authors': [author['name'] for author in entry['authors']],
            'categories': [tag['term'] for tag in entry['tags']],
            'abstract': entry['summary'].replace('\n', ' ').strip(),
            'published': entry['published'].split('T')[0],
        }
        results.append(result)

    return results



if __name__ == '__main__':
    results = search('styleGAN3')
    print(results[0])

    # result = fetch('2106.12423')
    # print(result)

    # results = fetchall(['2106.12423', '2303.08774'])
    # print(results)