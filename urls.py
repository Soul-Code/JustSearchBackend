from django.urls import path, include
from . import views

app_name = 'JustSearch'

urlpatterns_api = [
    path('login', views.login_view, name='login'),
    path('new_team', views.new_team, name='newteam'),
    path('get_team', views.get_team, name='getteam'),
    path('register', views.register, name='register'),
    path('get_rank', views.get_rank, name='getrank'),
    path('find_team', views.find_team, name='findteam'),
    path('join_team', views.join_team, name='join_team'),
    path('quit_team', views.quit_team, name='quit_team'),
    path('del_team', views.del_team, name='del_team'),
    path('logout', views.logout, name='logout'),

    path('get_questions', views.get_questions, name='get_questions'),
    path('get_questions/<int:page_num>', views.get_questions, name='get_questions'),
    path('submit_answer', views.submit_answer, name='submit_answer'),

    path('get_stages', views.get_stages, name='get_stages')
]

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(urlpatterns_api)),
    # 以上内容是just搜搜的嘤
    # 以下内容是迎新晚会的嘤
    path('<str:string>', views.index, name='index'),
    path('yxwh/<str:txt>', views.yxwh, name='yxwh')
]
