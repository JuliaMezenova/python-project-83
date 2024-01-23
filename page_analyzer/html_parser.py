from bs4 import BeautifulSoup


def get_tags_content_from_response(response):
    soup = BeautifulSoup(response.text, "html.parser")
    h1 = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''
    tag_description = soup.find('meta', attrs={'name': 'description'})
    if tag_description:
        description = tag_description.get('content')
    else:
        description = ''
    return {'h1': h1,
            'title': title,
            'description': description}
