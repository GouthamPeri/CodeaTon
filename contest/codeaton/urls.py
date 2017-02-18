from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.contest),
    url(r'^home', views.login_view)
]