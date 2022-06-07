from django.shortcuts import render
from feedsione.news.models import *
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, SearchHeadline
)


class SearchFeedResultsView(ListView):
    model = Feed
    template_name = 'search/search_feeds.html'
    context_object_name = 'feeds'
    paginate_by = 20


    def get_queryset(self):
        q = self.request.GET.get('q')

        query = SearchQuery(q)
        vector = SearchVector('title', 'feed_url')
        object_list = Feed.objects.annotate(
            rank = SearchRank(vector, query)
        ).filter(rank__gt=0).order_by('-rank')
        return object_list.prefetch_related('folders')

    def get_context_data(self, *arg, **kwargs):
        context = super(SearchFeedResultsView, self).get_context_data(*arg, **kwargs)
        context['folders'] = Folder.objects.filter(user=self.request.user)
        return context


class SearchArticleResultsView(ListView):
    model = Article
    template_name = 'search/search_articles.html'
    context_object_name = 'articles'
    paginate_by = 30


    def get_queryset(self):
        q = self.request.GET.get('q')

        query = SearchQuery(q)
        vector = SearchVector('title', 'description')

        # get subscribed feeds
        feeds = Feed.objects.filter(folders__user=self.request.user).distinct()
        object_list = Article.objects.filter(feed__in=feeds).annotate(
                                        rank=SearchRank(vector, query),
                                        headline=SearchHeadline(
                                                'title',
                                                query,
                                                start_sel='<span class="cbg-info">',
                                                stop_sel='</span>',
                                            )
                                    ).filter(
                                        rank__gt=0
                                    ).order_by('-rank')
        return object_list


