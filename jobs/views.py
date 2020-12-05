import sys
import requests
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import JobPost
from bs4 import BeautifulSoup as bs


def index(request):
    query = request.GET.get('q', '')
    if query:
        queryset = (Q(title__icontains=query))
        query_results = JobPost.objects.filter(queryset)
        if query_results:
            print('rendering jobs from DB', file=sys.stderr)
            paginator = Paginator(query_results, 5)

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'index.html', {'results': query_results, 'query': query, 'page_obj': page_obj})
        else:
            results = []
            r = requests.get('https://stackoverflow.com/jobs/feed?q=' + query)
            bs_content = bs(r.content, "xml")
            for item in bs_content.find_all("item")[:10]:
                items = {'guid': item.find("guid").get_text(), 'title': item.find("title").get_text(),
                         'description': item.find("description").get_text(), 'link': item.find("link").get_text(),
                         }
                results.append(items)

                for i in results:
                    current_posts = [p.id for p in JobPost.objects.all()]

                    if int(i['guid']) in current_posts:
                        print('got this job listing', file=sys.stderr)
                        pass
                    else:
                        JobPost.objects.create(
                            id=i['guid'],
                            title=i['title'],
                            description=i['description'],
                        )
                        print('create new job item', file=sys.stderr)
            new_queryset = (Q(title__icontains=query))
            results = JobPost.objects.filter(new_queryset)
            if results:
                print('rendering jobs from stack', file=sys.stderr)
                paginator = Paginator(new_queryset, 5)

                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                return render(request, 'index.html', {'results': results, 'query': query, 'page_obj': page_obj})
            else:
                print('no jobs from stack..then it is from db', file=sys.stderr)
                pass

    return render(request, 'index.html', {'results': 'Search something please'})
