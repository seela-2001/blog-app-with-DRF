from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/',views.CustomUserCreate.as_view(),name='user_register'),
    path('all-users/',views.UsersList.as_view(),name='all_users'),
    path('update/<int:pk>/',views.UpdateUser.as_view(),name='update_user'),
    path('delete/<int:pk>/',views.DeleteUser.as_view()),
    path('my/<int:pk>/',views.RetrieveUser.as_view(),name='my_account'),
    path('logout/',views.BlackListTokenView.as_view(),name='blacklist'),
    path('search/<str:search_query>',views.search_for_authors,name='authors_search'),
    path('upload-photo/<int:pk>/',views.upload_photo,name='upload_photo'),
    path('delete-photo/<int:pk>/',views.delete_photo,name='delete_photo'),
    path('change-password/<int:pk>/',views.change_password,name='chango_password'),
]