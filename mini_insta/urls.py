from django.urls import path
from .views import *
from .views import UserRegistrationView, UserLoginView, ProfileListAPIView, ProfileDetailAPIView, ProfilePostsAPIView, ProfileFeedAPIView, CreatePostAPIView, WebRegisterView
from django.contrib.auth import views as auth_views


urlpatterns = [
    # map the URL (empty string) to the view
    path('', ProfileListView.as_view(), name="profiles"),
    path('profile/<int:pk>', ProfileView.as_view(), name="profile"),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name='create_post'),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name='followers'),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name='following'),
    path('profile/<int:pk>/feed', PostFeedListView.as_view(), name='feed'),
    path('profile/<int:pk>/search', SearchView.as_view(), name='search'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('show_all', ShowAllView.as_view(), name="show_all"),
    path('article/<int:pk>', ArticleView.as_view(), name='article'),
    # web auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', WebRegisterView.as_view(), name='register'),
    
    # auth API
    path('api/login/', UserLoginView.as_view(), name='api_login'),
    path('api/register/', UserRegistrationView.as_view(), name='api_register'),
    

    # profile API
    path('api/profiles/', ProfileListAPIView.as_view(), name='api_profiles'),
    path('api/profiles/<int:pk>/', ProfileDetailAPIView.as_view(), name='api_profile'),
    path('api/profiles/<int:pk>/posts/', ProfilePostsAPIView.as_view(), name='api_posts'),
    path('api/profiles/<int:pk>/feed/', ProfileFeedAPIView.as_view(), name='api_feed'),
    path('api/profiles/<int:pk>/posts/create/', CreatePostAPIView.as_view(), name='api_create_post'),
]