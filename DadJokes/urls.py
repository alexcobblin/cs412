from django.urls import path
from . import views

urlpatterns = [
    path('', views.RandomView.as_view(), name='random'),
    path('random', views.RandomView.as_view(), name='random-alt'),
    path('jokes', views.JokeListView.as_view(), name='jokes'),
    path('joke/<int:pk>', views.JokeView.as_view(), name='joke'),
    path('pictures', views.PictureListView.as_view(), name='pictures'),
    path('picture/<int:pk>', views.PictureView.as_view(), name='picture'),

    path('api/', views.RandomJokeAPIView.as_view(), name='api-random'),
    path('api/random', views.RandomJokeAPIView.as_view(), name='api-random-alt'),
    path('api/jokes', views.JokeListAPIView.as_view(), name='api-jokes'),
    path('api/joke/<int:pk>', views.JokeDetailAPIView.as_view(), name='api-joke'),
    path('api/pictures', views.PictureListAPIView.as_view(), name='api-pictures'),
    path('api/picture/<int:pk>', views.PictureDetailAPIView.as_view(), name='api-picture'),
    path('api/random_picture', views.RandomPictureAPIView.as_view(), name='api-random-picture'),
]