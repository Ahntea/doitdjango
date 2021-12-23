from django.urls import path
from . import views

urlpatterns = [
    # path('<int:pk>/', views.single_post_page),
    # path("", views.index),
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('tag/<str:slug>/', views.tag_page),
    path('create_post/', views.PostCreate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('<int:pk>/new_comment/', views.new_comment),
    
    
    path('login/', views.kakao_login),
    path('users/login/kakao/callback', views.kakao_callback),
]
