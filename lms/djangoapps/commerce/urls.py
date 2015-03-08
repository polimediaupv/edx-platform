"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from .views import PurchaseView

urlpatterns = patterns(
    '',
    url(r'^purchase/$', PurchaseView.as_view(), name="purchase"),
)
