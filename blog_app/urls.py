from django.urls import path
from . import views

app_name = 'blog_app'

urlpatterns = [
    path('blog', views.blog_post_list_view, name='blog_post_list_view'),
    path('create/', views.blog_post_create_view, name='blog_post_create_view'),
    path('<int:id>/', views.blog_post_detail_view, name='blog_post_detail_view'),
]