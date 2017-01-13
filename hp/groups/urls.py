from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'groups'
urlpatterns = [
    url(r'^$',			views.GroupView.as_view(),	name='detail'		),
    url(r'^ownership/$',	views.OwnershipView.as_view(),	name='ownership'	),
    url(r'^membership/$',	views.MembershipView.as_view(),	name='membership'	),
    url(r'^create/$',		views.CreateView.as_view(),	name='create'		),
]
