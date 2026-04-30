# models.py
# Author: Alexander Cobb
# Description: Data models for TradingCG, a Pokémon card trading web application.

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable



class User(models.Model):
    '''A trader profile linked to a Django auth account.'''

    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    email = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)
    zip_code = models.TextField(blank=True)

    # Lat/lng populated from zip_code on save, used for distance sorting
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        '''Return string representation of the user.'''
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        '''Return the URL for this user's profile page.'''
        return reverse('show_user', kwargs={'pk': self.pk})

    def get_listings(self):
        '''Return all active trade listings for this user.'''
        return Listing.objects.filter(user=self)

    def get_collection(self):
        '''Return all CollectionCard records owned by this user.'''
        return CollectionCard.objects.filter(user=self).select_related('card')

    def get_trade_requests(self):
        '''Return all trade requests this user has sent.'''
        return TradeRequest.objects.filter(requester=self)

    def get_incoming_trades(self):
        '''Return all trade requests on this user's listings.'''
        return TradeRequest.objects.filter(listing__user=self)

    def distance_to(self, other):
        '''
        Return the approximate distance in miles to another User,
        using the Haversine formula. Returns inf if either user
        has no coordinates (sorts to the end of distance-sorted lists).
        '''
        if None in (self.latitude, self.longitude, other.latitude, other.longitude):
            return float('inf')

        R = 3958.8  # Earth radius in miles
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return R * 2 * math.asin(math.sqrt(a))
    def save(self, *args, **kwargs):
        # Only geocode if we have a zip and no coordinates yet
        if self.zip_code and (self.latitude is None or self.longitude is None):
            lat, lng = zip_to_lat_lng(self.zip_code)
            self.latitude = lat
            self.longitude = lng

        super().save(*args, **kwargs)

geolocator = Nominatim(user_agent="pokemon_trader_app")

def zip_to_lat_lng(zip_code):
    try:
        location = geolocator.geocode({"postalcode": zip_code, "country": "USA"})
        if location:
            return location.latitude, location.longitude
    except GeocoderUnavailable:
        pass
    return None, None

class Card(models.Model):
    '''
    A Pokémon card in the shared catalog.
    Does not require any foreign keys — stands alone as a reference record.
    '''

    name = models.TextField(blank=False)
    set_name = models.TextField(blank=True)
    rarity = models.TextField(blank=True)

    def __str__(self):
        '''Return the card name and set.'''
        return f'{self.name} ({self.set_name})'


class CollectionCard(models.Model):
    '''
    Represents a physical card that a specific user owns.
    Separate from Listing — a user can own a card without trading it.
    Foreign keys: User, Card.
    '''

    CONDITION_CHOICES = [
        ('mint', 'Mint'),
        ('near_mint', 'Near Mint'),
        ('played', 'Played'),
        ('heavily_played', 'Heavily Played'),
    ]

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='collection')
    card = models.ForeignKey("Card", on_delete=models.CASCADE)
    condition = models.TextField(choices=CONDITION_CHOICES, blank=False, default='near_mint')
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        '''Prevent duplicate card+user combos — use quantity instead.'''
        unique_together = ('user', 'card')

    def __str__(self):
        '''Return a description of this collection entry.'''
        return f'{self.user} owns {self.quantity}x {self.card.name}'

    def is_listed(self):
        '''Return True if this card is currently listed for trade by this user.'''
        return Listing.objects.filter(user=self.user, card=self.card).exists()

    def get_listing(self):
        '''Return the active Listing for this card, or None.'''
        return Listing.objects.filter(user=self.user, card=self.card).first()


class Listing(models.Model):
    '''
    A card a user wants to trade publicly.
    Foreign keys: User, Card.
    '''

    CONDITION_CHOICES = [
        ('mint', 'Mint'),
        ('near_mint', 'Near Mint'),
        ('played', 'Played'),
        ('heavily_played', 'Heavily Played'),
    ]

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    card = models.ForeignKey("Card", on_delete=models.CASCADE)
    condition = models.TextField(choices=CONDITION_CHOICES, blank=False, default='near_mint')
    caption = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string description of the listing.'''
        return f'{self.card.name} listed by {self.user}'

    def get_absolute_url(self):
        '''Return the URL for this listing's detail page.'''
        return reverse('listing', kwargs={'pk': self.pk})

    def get_all_photos(self):
        '''Return all photos for this listing ordered by upload time.'''
        return Photo.objects.filter(listing=self).order_by('timestamp')

    def get_front_photo(self):
        '''Return the first uploaded photo (front of card).'''
        return Photo.objects.filter(listing=self).order_by('timestamp').first()

    def get_back_photo(self):
        '''Return the last uploaded photo (back of card).'''
        return Photo.objects.filter(listing=self).order_by('timestamp').last()

    def get_trade_requests(self):
        '''Return all trade requests for this listing.'''
        return TradeRequest.objects.filter(listing=self)


class Photo(models.Model):
    '''
    A photo of a card attached to a specific Listing.
    Foreign key: Listing.
    '''

    listing = models.ForeignKey("Listing", on_delete=models.CASCADE)
    image_file = models.ImageField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string description of this photo.'''
        return f'Photo for Listing {self.listing.pk} at {self.timestamp}'

    def get_image_url(self):
        '''Return the URL to the uploaded image file.'''
        return self.image_file.url


class TradeRequest(models.Model):
    '''
    A request by one user to trade for another user's listed card.
    Foreign keys: User (as requester), Listing, CollectionCard (offered card).
    '''

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]

    requester = models.ForeignKey("User", on_delete=models.CASCADE, related_name='sent_requests')
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE)
    offered_card = models.ForeignKey("CollectionCard", on_delete=models.SET_NULL, null=True, blank=True, related_name='trade_offers')
    status = models.TextField(choices=STATUS_CHOICES, blank=False, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string description of this trade request.'''
        return f'{self.requester} requested trade for {self.listing} — {self.status}'

    def get_absolute_url(self):
        '''Return the URL for this trade request's detail page.'''
        return reverse('show_trade', kwargs={'pk': self.pk})

    def is_accepted(self):
        '''Return True if this trade has been accepted.'''
        return self.status == 'accepted'