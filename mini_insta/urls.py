from django.urls import path
from .views import ShowAllView, ArticleView, RandomArticleView, ProfileListView, ProfileView # our view class definition 
 
 
urlpatterns = [
    # map the URL (empty string) to the view
    path('', ProfileListView.as_view(), name="profiles"),
    path('profile/<int:pk>', ProfileView.as_view(), name="profile"),
    path('show_all', ShowAllView.as_view(), name="show_all"),
    path('article/<int:pk>', ArticleView.as_view(), name='article'), # show one article ### NEW
]