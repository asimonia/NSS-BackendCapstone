from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from tracks.views import CourseListView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^course/', include('tracks.urls')),
    url(r'^students/', include('students.urls')),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^$', CourseListView.as_view(), name='course_list'),
]
