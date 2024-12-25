from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'users'

router = DefaultRouter()
router.register(r'users',views.UserViewSet,basename='user')


urlpatterns = [
    path('',include(router.urls)),
    path('logout/',views.BlackListTokenView.as_view(),name='blacklist'),
    path('search/<str:search_query>',views.search_for_authors,name='authors_search'),
    path('change-password/<int:pk>/',views.change_password,name='chango_password'),
]