from django.conf.urls import url

from . import views

app_name = 'groups'

urlpatterns = [
    url(r'^$',                                views.OverView.as_view(),        name='overview'   ),
    url(r'^ownership/$',                      views.OwnershipView.as_view(),   name='ownership'  ),
    url(r'^membership/$',                     views.MembershipView.as_view(),  name='membership' ),
    url(r'^create/$',                         views.CreateGroupView.as_view(), name='create'     ),
    url(r'^details/(?P<pk>\d+)/$',            views.GroupView.as_view(),       name='details'    ),
    url(r'^edit/(?P<pk>\d+)/$',               views.EditView.as_view(),        name='edit'       ),
    url(r'^leave/(?P<pk>\d+)/$',              views.LeaveView.as_view(),       name='leave'      ),
    url(r'^delete/(?P<pk>\d+)/$',             views.DeleteView.as_view(),      name='delete'     ),
    url(r'^admin/sync/(?P<action>\w{2,4})/$', views.SyncView,                  name='sync'       ),
]
