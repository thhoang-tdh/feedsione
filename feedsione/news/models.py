from distutils.command.upload import upload
from tabnanny import verbose
from time import mktime
from django.db import models
import uuid
from datetime import datetime, timezone
from django.utils import timezone as tz
import feedparser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify, truncatewords_html
from django.urls import reverse
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
import requests
from feedsione.users.models import User


def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)

def fifteen_hence():
    return timezone.now() + timezone.timedelta(minutes=15)

class Source(models.Model):
    """
    Source, group, or website domain of multiple RSS feeds
    """
    name = models.URLField(
        verbose_name=_('source name'),
        max_length=50,
        unique=True
    )
    logo_url = models.URLField(
        verbose_name=_('logo url'),
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
class Topic(models.Model):
    """
    Topic, search keyword, tag, filter,...
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Feed(models.Model):

    feed_url = models.URLField(
        verbose_name=_('feed URL'),
        unique=True,
        max_length=255,
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=200,
        blank=True
    )
    site_url = models.URLField(
        verbose_name=_('site URL'),
        blank=True,
        null=True
    )

    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    date_created = models.DateTimeField(verbose_name=_('date created'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('date modified'), auto_now=True)
    date_last_fetch = models.DateTimeField(verbose_name=_('date of last fetch'), auto_now=True)
    frequency = models.IntegerField(verbose_name=_('frequency'), default=10)   # TODO: recheck this, frequency of refresh

    topics = models.ManyToManyField(Topic, blank=True)
    source = models.ForeignKey(
        Source,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="feeds"
    )

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('id', )

    def __str__(self):
        return self.title

    def clean(self):
        parsed_data = feedparser.parse(self.feed_url)
        if not parsed_data or parsed_data.bozo:
            raise ValidationError({'feed_url': 'Invalid RSS feed url'})
        else:
            self.parsed_rss_url = parsed_data
        # try:
        #     r = requests.get(self.feed_url)
        #     parsed_data = feedparser.parse(r.content)

        #     if not parsed_data or parsed_data.bozo:
        #         raise ValidationError(
        #             {'feed_url': 'Invalid RSS feed url'}
        #         )
        #     else:
        #         self.parsed_rss_url = parsed_data

        # except:
        #     raise ValidationError(
        #         {'feed_url': 'Invalid RSS feed url or page cant reach'}
        #     )

    def save(self, *args, **kwargs):

        if self.parsed_rss_url:
            data = self.parsed_rss_url
        else:
            data = feedparser.parse(self.feed_url)

        if data.feed.title:
            self.title = data.feed.title
        else:
            self.title = 'Undefined'

        if data.feed.link:
            self.site_url = data.feed.link

            # get or create source
            netloc = urlparse(data.feed.link).netloc

            if not self.source and netloc and len(netloc) > 0:
                try:
                    source = Source.objects.get(name=netloc)
                except:
                    source = Source.objects.create(name=netloc)

                self.source = source

        super(Feed, self).save(*args, **kwargs)

    def download_feed_articles(self):
        """ Download articles from current feed."""
        try:
            # r = requests.get(self.feed_url)
            # data = feedparser.parse(r.content)
            data = feedparser.parse(self.feed_url)
            for entry in data.entries:
                try:
                    article = Article.objects.get(link=entry.link)
                    continue
                except:
                    article = Article()

                article.feed = self
                article.description = entry.description
                article.truncated_description = truncatewords_html(entry.description, 50)
                article.link = entry.link
                article.title = entry.title

                try:
                    date_published = entry.published_parsed
                except:
                    try:
                        date_published = entry.created_parsed
                    except:
                        date_published = entry.updated_parsed

                article.date_published = datetime.fromtimestamp(mktime(date_published), timezone.utc)
                article.save()

            self.date_last_fetch =  tz.now()
            self.save()
        except Exception as e:
            pass


class Folder(models.Model):
    """
    User defined folder, buddle or collection of feeds
    """
    name = models.CharField(
        verbose_name=_('folder name'),
        max_length=50,
        blank=False, null=False,
    )
    user = models.ForeignKey(
        User,
        related_name="folders",
        on_delete=models.CASCADE
    )
    is_public = models.BooleanField(verbose_name=_('is public'), default=False)
    feeds = models.ManyToManyField(Feed, blank=True)
    date_created = models.DateTimeField(verbose_name=_('date created'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('date modified'), auto_now=True)


class Article(models.Model):
    guid = models.UUIDField(default=uuid.uuid4)

    title = models.CharField(verbose_name=_('article title'), max_length=255)
    description = models.TextField(verbose_name=_('description'))
    truncated_description = models.TextField(
        verbose_name=_('truncated description'),
        blank=True, null=True,
    )
    link = models.URLField(
        verbose_name=_('article link'),
        unique=True,
        max_length=2048
    ) # link to original article
    slug = models.SlugField(unique=True, null=True, max_length=255)
    date_published = models.DateTimeField(verbose_name=_('date published'))

    feed = models.ForeignKey(
        Feed,
        related_name='articles',
        on_delete=models.CASCADE
    )

    topics = models.ManyToManyField(Topic, blank=True)
    read_later = models.ManyToManyField(User, through='ReadLater', blank=True)

    class Meta:
        # ordering? it affects performance
        # ordering = ('-date_published')
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return reverse('news:article_detail', kwargs={'slug': self.slug, 'guid': str(self.guid)})
        return reverse('news:article_detail', kwargs={'slug': self.slug})
        # return reverse('', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.slug:
            new_slug = str(self.guid) + '-' + slugify(self.title)
            self.slug = new_slug[:255]

        super(Article, self).save(*args, **kwargs)


class ReadLater(models.Model):
    """
    Read Later articles
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        auto_now_add=True
    )

    class Meta:
        unique_together = [['user', 'article']]







