

from __future__ import absolute_import, unicode_literals

from datetime import timedelta
from re import T
from django.utils import timezone
from time import sleep
from celery import shared_task
from django.core.cache import cache
from celery.utils.log import get_task_logger
from config import celery_app

from feedsione.news.models import Feed

logger = get_task_logger(__name__)


@celery_app.task(
)
def get_articles(feed_id):

    logger.debug('Importing feed: %s', str(feed_id))
    log_id = f'lock_get_feed_articles_{feed_id}'

    with cache.lock(
        log_id,
        timeout=5*60,
        blocking_timeout=1,
    ) as acquired:
        if acquired:
            feed = Feed.objects.get(id=feed_id)
            logger.info('Retrieving articles for feed: ' + feed.title)
            return feed.download_feed_articles()
    logger.debug(f'Feed {feed_id} is aldready being used by another worker')


@celery_app.task(
)
def retrieve_new_feed_articles():
    # update feed article task : Periodic task for 15, 30, 60 mins??
    """ Retrieve new articles from all RSS feeds """
    feeds = Feed.objects.all()

    count = 0
    for feed in feeds:
        # if feed.is_active and timezone.now() <= feed.date_last_fetch + timedelta(minutes=feed.frequency):
        #     get_articles.apply_async(args=(feed.id,), retry=False)
        get_articles.apply_async(args=(feed.id,), retry=False)
        count += 1

    return f"Processed {count} feeds"
