from django.shortcuts import render
from feedsione.news.models import *
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank
)


class SearchFeedResultsView(ListView):
    model = Feed
    template_name = 'search/search_results.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        query = self.request.GET.get('q')

        query = SearchQuery(query)
        vector = SearchVector('title', 'feed_url')
        object_list = Feed.objects.annotate(
            rank = SearchRank(vector, query)
        ).filter(rank__gt=0).order_by('-rank')
        return object_list


class SearchArticleResultsView(ListView):
    model = Article
    template_name = 'search/search_article_results.html'
    context_object_name = 'articles'

    def get_queryset(self):
        query = self.request.GET.get('q')

        query = SearchQuery(query)
        vector = SearchVector('title', 'description')

        # get subscribed feeds
        feeds = Feed.objects.filter(folders__user=self.request.user).distinct()
        object_list = Article.objects.filter(feed__in=feeds).annotate(
                                        rank=SearchRank(vector, query)
                                    ).filter(
                                        rank__gt=0
                                    ).order_by('-rank')
        return object_list






# Book.objects.annotate(
#     rank=SearchRank(vector, query)
# )filter(rank__gte=0.3).order_by('-rank')


# from django.contrib.postgres.search import (
#     SearchVector, SearchQuery, SearchRank
# )
# from django.views.generic import FormView, ListView
# from .forms import SearchForm
# from .models import City

# class HomepageView(FormView):
#     template_name = 'home.html'
#     form_class = SearchForm

# class SearchResultsView(ListView):
#     model = City
#     template_name = 'search_results.html'

#     ## SearchRank ##
#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         vector = SearchVector('state')
#         search_query = SearchQuery(query)
#         object_list = City.objects.annotate(
#             rank=SearchRank(vector, search_query)
#         ).order_by('-rank')
#         return object_list

    ## SearchQuery ##
    # def get_queryset(self):
    #     query = self.request.GET.get('q')
    #     object_list = City.objects.annotate(
    #         search=SearchVector('name', 'state'),
    #     ).filter(search=SearchQuery(query))
    #     return object_list

    ## SearchVector ##
    # def get_queryset(self):
    #     query = self.request.GET.get('q')
    #     object_list = City.objects.annotate(
    #         search=SearchVector('name', 'state'),
    #     ).filter(search=query)
    #     return object_list


    # https://www.youtube.com/watch?v=is3R8d420D4&t=1325s&ab_channel=DjangoConUS