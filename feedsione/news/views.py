from django.shortcuts import render

from feedsione.news.models import *
from feedsione.news.forms import *
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from datetime import timedelta
from django.utils import timezone
from itertools import chain
from django.http import HttpResponseRedirect



class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 50
    ordering = ['-date_published']

    def get_context_data(self, *arg, **kwargs):
        context = super(ArticleListView, self).get_context_data(*arg, **kwargs)
        context['folders'] = Folder.objects.filter(user=self.request.user)
        context['page_header'] = 'Articles'

        return context


class AllArticlesView(ArticleListView):
    def get_queryset(self):
        pass
        qs = super().get_queryset()
        articles = qs.filter(
            feed__in=Feed.objects.filter(users=self.request.user).
                                    distinct())
        return articles

    def get_context_data(self, *arg, **kwargs):
        context = super(AllArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'All articles'
        return context


class TodayArticlesView(AllArticlesView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(date_published__gt=timezone.now()-timedelta(hours=24))

    def get_context_data(self, *arg, **kwargs):
        context = super(TodayArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Today'
        return context


class ReadLaterArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(userarticle__user=self.request.user,
                        userarticle__is_read_later=True)

    def get_context_data(self, *arg, **kwargs):
        context = super(ReadLaterArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Read later'
        return context


class FeedArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.feed = get_object_or_404(Feed, slug=slug)
        articles = qs.filter(feed=self.feed)
        return articles

    def get_context_data(self, *arg, **kwargs):
        context = super(FeedArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.feed.title
        return context


class FolderArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.folder = get_object_or_404(Folder, slug=slug)
        articles = qs.filter(feed__in=Feed.objects.filter(users=self.request.user,
                                                         folders=self.folder)
                                                        .distinct())
        return articles

    def get_context_data(self, *arg, **kwargs):
        context = super(FolderArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.folder.name
        return context



# TODO:
class FeedListView(ListView):
    model = Feed
    template_name = 'news/feed_list.html'
    context_object_name = 'feeds'
    ordering = ['title']









class FolderCreateView(LoginRequiredMixin, CreateView):
    # model = Folder
    template_name = 'news/create_folder.html'
    form_class = FolderCreateForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def get_initial(self, *args, **kwargs):
        initial = super(FolderCreateView, self).get_initial(**kwargs)
        initial['name'] = 'My folder'
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FolderCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class FeedCreateView(LoginRequiredMixin, CreateView):
    template_name = 'news/create_feed.html'
    form_class = FeedCreateForm

    def form_valid(self, form):
        feed = form.save()
        return HttpResponseRedirect(feed.get_absolute_url() + 'follow/')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FeedCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs



# class FeedFollowView(LoginRequiredMixin, CreateView):
#     template_name = 'news/feed_follow_addfolder.html'
































