from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'blog_api'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'posts', views.PostViewSet, basename='post')
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    views.CommentViewSet,
    basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('all-my-posts/', views.AuthorPostsView.as_view(), name='my_posts'),
    path('search/<str:search_query>/', views.search_for_blog, name='search'),
]
