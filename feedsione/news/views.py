from django.shortcuts import render

from feedsione.news.models import Article, Feed
from django.views.generic import ListView, DetailView

class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 50
    ordering = ['date_published']




class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'