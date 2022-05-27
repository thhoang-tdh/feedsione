from dataclasses import fields
import json
from django.shortcuts import render, redirect

from feedsione.news.models import *
from feedsione.news.forms import *
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from datetime import timedelta
from django.utils import timezone
from itertools import chain
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import F


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            is_read=F('userarticle__is_read'),
            is_read_later=F('userarticle__is_read_later'),
            is_saved=F('userarticle__is_saved')
        )

    def get_context_data(self, *arg, **kwargs):
        context = super(ArticleListView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Articles'
        return context

    def get_ordering(self):
        self.ordering = '-date_published'

        ordering = self.request.GET.get('o')
        if ordering is not None:
            field_names = [a.name for a in Article._meta.fields]
            ordering_opts = tuple(set(ordering.split(',')) & set(field_names))
            if ordering_opts:
                self.ordering = ordering_opts

        return self.ordering

    def qs_extra(self, qs):
        '''
        Filter out articles that is marked as read/unread from queryset.
        Return unread articles by default.
        '''
        is_unread = self.request.GET.get('unread')
        if is_unread is not None:
            if is_unread == '0': # return all articles (includes read and unread)
                return qs
        return qs.exclude(is_read=True)

    def post(self, *args, **kwargs):
        markread_form = MarkReadForm(self.request.POST or None)
        if markread_form.is_valid():
            day = markread_form.cleaned_data.get('day')
            articles = self.get_queryset()
            if day > 0:
                articles = articles.filter(date_published__lt=timezone.now()-timedelta(days=day))
            for article in articles:
                UserArticle.objects.update_or_create(user=self.request.user,
                                                        article=article,
                                                        is_read=True)
            return HttpResponseRedirect(self.request.path_info + '?unread=1')
        return HttpResponseRedirect(self.request.path_info)



class AllArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        subscripted_feeds = Feed.objects.filter(folders__user=self.request.user).distinct()
        qs = qs.filter(feed__in=subscripted_feeds)

        return self.qs_extra(qs)

    def get_context_data(self, *arg, **kwargs):
        context = super(AllArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'All articles'
        return context


class TodayArticlesView(AllArticlesView):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(date_published__gt=timezone.now()-timedelta(hours=24))

        return self.qs_extra(qs)

    def get_context_data(self, *arg, **kwargs):
        context = super(TodayArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Today'
        return context

class ReadLaterArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(userarticle__user=self.request.user,
                       userarticle__is_read_later=True)

        return self.qs_extra(qs)

    def get_context_data(self, *arg, **kwargs):
        context = super(ReadLaterArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Read later'
        return context


class FeedArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.feed = get_object_or_404(Feed, slug=slug)
        qs = qs.filter(feed=self.feed)

        return self.qs_extra(qs)

    def get_context_data(self, *arg, **kwargs):
        context = super(FeedArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.feed.title
        return context


class FolderArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.folder = get_object_or_404(Folder, slug=slug, user=self.request.user)
        qs = qs.filter(feed__in=self.folder.feeds.all())

        return self.qs_extra(qs)

    def get_context_data(self, *arg, **kwargs):
        context = super(FolderArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.folder.name
        return context


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
        return HttpResponseRedirect(feed.get_absolute_url())

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FeedCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


@login_required
def follow_feed(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            user = request.user
            data = request.POST
            feed = Feed.objects.filter(slug=data['feed_slug']).first()
            folder = Folder.objects.filter(slug=data['folder_slug']).first()
            if feed is None or folder is None:
                return JsonResponse({'msg': 'Invalid request'}, status=400)

            FeedSubscription.objects.get_or_create(user=user, feed=feed, folder=folder)
            return JsonResponse({'msg': 'Subscription added!'})

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def unfollow_feed(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'DELETE':
            user = request.user
            data = request.DELETE
            feed = Feed.objects.filter(slug=data['feed_slug']).first()
            folder = Folder.objects.filter(slug=data['folder_slug']).first()

            fs = FeedSubscription.objects.filter(user=user, feed=feed, folder=folder).first()
            if not fs is None:
                fs.delete()

            return JsonResponse({'msg': 'Successfully unfollow feed!'})

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def mark_as_read(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = MarkAsReadArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_read = form.cleaned_data.get('is_read')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_read=form.cleaned_data.get('is_read'))
                ua.save()
                return JsonResponse({'msg': 'OK'})

            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def add_readlater(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = ReadLaterArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_read_later = form.cleaned_data.get('is_read_later')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_read_later=form.cleaned_data.get('is_read_later'))
                ua.save()

                return JsonResponse({'msg': 'OK'})
            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')



@login_required
def save_article(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = SaveArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_saved = form.cleaned_data.get('is_saved')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_saved=form.cleaned_data.get('is_saved'))
                ua.save()

                return JsonResponse({'msg': 'OK'})
            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')