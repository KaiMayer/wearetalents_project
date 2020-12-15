import sys
import requests
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db import IntegrityError
from .models import JobPost
from bs4 import BeautifulSoup as bs
from django.db import connection
from urllib.request import pathname2url


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def paginate(request, results):
    paginator = Paginator(results, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    query = request.GET.get('q', '')
    link_query = pathname2url(query)

    if query:

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM search WHERE title MATCH '\"%s\"*' " % query)
        query_results = dictfetchall(cursor)

        if len(query_results) > 10:
            print('rendering jobs from DB', file=sys.stderr)
            page_obj = paginate(request, query_results)

            return render(request, 'index.html', {'results': query_results, 'link_query': link_query,
                                                  'query': query, 'page_obj': page_obj})
        else:
            results = []
            r = requests.get('https://stackoverflow.com/jobs/feed?q=' + query)
            bs_content = bs(r.content, "xml")

            for item in bs_content.find_all("item")[:200]:
                items = {'guid': item.find("guid").get_text(),
                         'title': item.find("title").get_text(),
                         'description': item.find("description").get_text(),
                         'link': item.find("link").get_text(),
                         'updated_date': item.find("updated").get_text(),
                         'author': item.find("author").get_text(),
                         'location': item.find('location xmlns'),
                         }
                results.append(items)

                for i in results:
                    try:
                        JobPost.objects.create(
                            id=i['guid'],
                            title=i['title'],
                            description=i['description'],
                            link=i['link'],
                            updated_date=i['updated_date'],
                            location=i['location'],
                            author=i['author'],
                        )
                    except IntegrityError as e:
                        if 'unique constraint' in e.args:
                            continue
                        pass

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM search WHERE title MATCH '\"%s\"*' " % query)
            results = dictfetchall(cursor)

            if results:
                page_obj = paginate(request, results)

                return render(request, 'index.html', {'results': results, 'link_query': link_query,
                                                      'query': query, 'page_obj': page_obj})
            else:
                return render(request, 'index.html', {'query': query})

    return render(request, 'index.html')
