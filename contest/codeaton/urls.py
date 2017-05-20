from . import views
from django.conf.urls import url

urlpatterns = [
    #url(r'^$', views.contest),
    url(r'^home', views.login_view),
    url(r'^main_ques', views.contest),
    url(r'^questions', views.questions),
    # url(r'^header', views.header),
]