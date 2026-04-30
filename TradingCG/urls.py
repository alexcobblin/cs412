# urls.py
# URL routing for the TradingCG app.

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Listings
    path('', views.AllListingsView.as_view(), name='all_listings'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='listing'),
    path('listing/random/', views.RandomListingView.as_view(), name='random_listing'),
    path('listing/create/', views.CreateListingView.as_view(), name='create_listing'),
    path('listing/<int:pk>/update/', views.UpdateListingView.as_view(), name='update_listing'),
    path('listing/<int:pk>/delete/', views.DeleteListingView.as_view(), name='delete_listing'),

    # Collection
    path('collection/', views.collection_view, name='collection'),

    # Users
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='show_user'),
    path('user/<int:pk>/update/', views.UpdateUserView.as_view(), name='update_user'),

    # Cards
    path('card/<int:pk>/', views.CardDetailView.as_view(), name='show_card'),
    path('card/create/', views.CreateCardView.as_view(), name='create_card'),

    # Photos
    path('photo/add/', views.AddPhotoView.as_view(), name='add_photo'),

    # Trade Requests
    path('trade/<int:pk>/', views.TradeRequestDetailView.as_view(), name='show_trade'),
    path('trade/create/<int:listing_pk>/', views.create_trade_view, name='create_trade'),
    path('trade/<int:pk>/update/', views.UpdateTradeRequestView.as_view(), name='update_trade'),
    path('trade/<int:pk>/cancel/', views.cancel_trade_view, name='cancel_trade'),
]