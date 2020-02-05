from django.urls import path

from . import views

urlpatterns = [ 
    path('', views.get_tickers, name='search'),
    path(r'detail/', views.tickers, name='tickers'),
    path(r'detail/<str:ticker>', views.filings, name='filings'),
    path(r'detail/<str:ticker>/<str:accession>', views.detail, name='details')
]
