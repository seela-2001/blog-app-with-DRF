from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'blog_api'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'posts', views.PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)), 
    path('all-my-posts/',views.AuthorPostsView.as_view(),name='my_posts'),
    path('search/<str:search_query>/', views.search_for_blog, name='search'),
    path('create-comment/<int:post_id>/',views.CreateComment.as_view(),name='create comment'),
    path('post-comments/<int:post_id>/',views.RetrieveAllPostComments.as_view(),name='all-post-comments'),
    path('delete-comment/<int:post_id>/<int:comment_id>/',views.DeletePostComment.as_view(),name='delete-comment'),
    path('update-comment/<int:post_id>/<int:comment_id>/',views.UpdatePostComment.as_view(),name='update-comment'),
]
