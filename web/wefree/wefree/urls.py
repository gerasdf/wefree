from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'wefree.core.views.index', name='index'),
    url(r'^get/$', 'wefree.core.views.get', name='get'),
    url(r'^report/$', 'wefree.core.views.report', name='report'),
    url(r'^crawl/$', 'wefree.core.views.comunity_crawl', name='comunity_crawl'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
