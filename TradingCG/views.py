import random
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse, reverse_lazy
from django import forms
from .models import Listing, User, Card, Photo, TradeRequest, CollectionCard


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_profile(request):
    '''Return the User profile for the logged-in auth user, or None.'''
    if request.user.is_authenticated:
        try:
            return request.user.profile
        except User.DoesNotExist:
            return None
    return None


def geocode_zip(zip_code):
    '''
    Return (latitude, longitude) for a US zip code using the free Census API.
    Returns (None, None) if lookup fails.
    '''
    import urllib.request, json
    try:
        url = (
            f'https://geocoding.geo.census.gov/geocoder/locations/address'
            f'?zip={zip_code}&benchmark=2020&format=json'
        )
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
        coords = data['result']['addressMatches'][0]['coordinates']
        return coords['y'], coords['x']  # lat, lng
    except Exception:
        return None, None


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get('next', reverse('all_listings')))
    else:
        form = AuthenticationForm()
    return render(request, 'TradingCG/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('all_listings')


# ---------------------------------------------------------------------------
# Signup — creates both an AuthUser and a linked User profile
# ---------------------------------------------------------------------------

class SignupForm(forms.Form):
    username   = forms.CharField(max_length=150)
    password1  = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2  = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    first_name = forms.CharField(max_length=100)
    last_name  = forms.CharField(max_length=100)
    email      = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    zip_code   = forms.CharField(max_length=10, required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        if AuthUser.objects.filter(username=cleaned.get('username')).exists():
            raise forms.ValidationError('That username is already taken.')
        return cleaned


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            auth_user = AuthUser.objects.create_user(
                username=d['username'],
                password=d['password1'],
            )
            lat, lng = geocode_zip(d.get('zip_code', ''))
            profile = User.objects.create(
                auth_user=auth_user,
                first_name=d['first_name'],
                last_name=d['last_name'],
                email=d.get('email', ''),
                phone_number=d.get('phone_number', ''),
                zip_code=d.get('zip_code', ''),
                latitude=lat,
                longitude=lng,
            )
            login(request, auth_user)
            return redirect('show_user', pk=profile.pk)
    else:
        form = SignupForm()
    return render(request, 'TradingCG/signup.html', {'form': form, 'title': 'Sign Up'})


# ---------------------------------------------------------------------------
# Listing views
# ---------------------------------------------------------------------------

class AllListingsView(ListView):
    '''Show all listings, sorted by distance if the user is logged in.'''
    model = Listing
    template_name = 'TradingCG/all_listings.html'
    context_object_name = 'listings'

    def get_queryset(self):
        profile = get_profile(self.request)
        listings = list(Listing.objects.select_related('user', 'card').all())

        if profile and profile.latitude:
            for listing in listings:
                # If listing user has no coordinates → send to bottom
                if listing.user.latitude is None:
                    listing.distance = 999999
                else:
                    listing.distance = profile.distance_to(listing.user)

            listings.sort(key=lambda l: l.distance)

        return listings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self.request)
        return context


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'TradingCG/listing.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.get_object().get_all_photos()
        context['profile'] = get_profile(self.request)
        return context


class RandomListingView(DetailView):
    model = Listing
    template_name = 'TradingCG/listing.html'
    context_object_name = 'listing'

    def get_object(self):
        all_listings = list(Listing.objects.all())
        if not all_listings:
            return None
        return random.choice(all_listings)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.get_object()
        context['photos'] = listing.get_all_photos() if listing else []
        context['profile'] = get_profile(self.request)
        return context


class CreateListingView(LoginRequiredMixin, CreateView):
    '''
    Create a listing. Auto-populates user from session.
    Card dropdown is filtered to only cards the logged-in user has added.
    '''
    model = Listing
    template_name = 'TradingCG/create_listing.html'
    fields = ['card', 'condition', 'caption']

    login_url = '/login/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show the logged-in user's own cards in the dropdown
        profile = get_profile(self.request)
        if profile:
            owned_card_ids = Listing.objects.filter(user=profile).values_list('card_id', flat=True)
            form.fields['card'].queryset = Card.objects.filter(pk__in=owned_card_ids)
        return form

    def form_valid(self, form):
        form.instance.user = get_profile(self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('listing', kwargs={'pk': self.object.pk})


class UpdateListingView(LoginRequiredMixin, UpdateView):
    model = Listing
    template_name = 'TradingCG/update_listing.html'
    fields = ['condition', 'caption']
    login_url = '/login/'

    def get_success_url(self):
        return reverse('listing', kwargs={'pk': self.object.pk})


class DeleteListingView(LoginRequiredMixin, DeleteView):
    model = Listing
    template_name = 'TradingCG/delete_listing.html'
    success_url = reverse_lazy('all_listings')
    login_url = '/login/'


# ---------------------------------------------------------------------------
# User / profile views
# ---------------------------------------------------------------------------

class UserDetailView(DetailView):
    model = User
    template_name = 'TradingCG/show_user.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        context['listings'] = Listing.objects.filter(user=profile_user)
        context['sent_requests'] = TradeRequest.objects.filter(requester=profile_user)
        context['profile'] = get_profile(self.request)
        return context


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'TradingCG/update_user.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'zip_code']
    login_url = '/login/'

    def form_valid(self, form):
        # Re-geocode if zip code changed
        user = form.save(commit=False)
        lat, lng = geocode_zip(user.zip_code)
        user.latitude = lat
        user.longitude = lng
        user.save()
        return redirect('show_user', pk=user.pk)


# ---------------------------------------------------------------------------
# Card views
# ---------------------------------------------------------------------------

class CardDetailView(DetailView):
    model = Card
    template_name = 'TradingCG/show_card.html'
    context_object_name = 'card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listings'] = Listing.objects.filter(card=self.get_object())
        return context


class CreateCardView(LoginRequiredMixin, CreateView):
    '''
    Creates a Card record. After creation, immediately creates a Listing
    so the card is associated with the logged-in user.
    '''
    model = Card
    template_name = 'TradingCG/create_card.html'
    fields = ['name', 'set_name', 'rarity']
    login_url = '/login/'

    def get_success_url(self):
        return reverse('show_card', kwargs={'pk': self.object.pk})


# ---------------------------------------------------------------------------
# Photo views
# ---------------------------------------------------------------------------

class AddPhotoView(LoginRequiredMixin, CreateView):
    model = Photo
    template_name = 'TradingCG/add_photo.html'
    fields = ['listing', 'image_file']
    login_url = '/login/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only allow adding photos to your own listings
        profile = get_profile(self.request)
        if profile:
            form.fields['listing'].queryset = Listing.objects.filter(user=profile)
        return form

    def get_success_url(self):
        return reverse('listing', kwargs={'pk': self.object.listing.pk})


# ---------------------------------------------------------------------------
# Collection views
# ---------------------------------------------------------------------------

@login_required(login_url='/login/')
def collection_view(request):
    '''
    Display the logged-in user's card collection.
    Handles adding cards to collection, removing them, and toggling listings,
    all from a single page via POST actions.
    '''
    profile = get_profile(request)

    # --- Handle POST actions ---
    if request.method == 'POST':
        action = request.POST.get('action')

        # Add a card to the collection (or increment quantity)
        if action == 'add_card':
            card_id = request.POST.get('card_id')
            condition = request.POST.get('condition', 'near_mint')
            card = get_object_or_404(Card, pk=card_id)
            obj, created = CollectionCard.objects.get_or_create(
                user=profile, card=card,
                defaults={'condition': condition}
            )
            if not created:
                obj.quantity += 1
                obj.save()

        # Add a brand-new card to the catalog AND the user's collection
        elif action == 'add_new_card':
            name = request.POST.get('name', '').strip()
            set_name = request.POST.get('set_name', '').strip()
            rarity = request.POST.get('rarity', '').strip()
            condition = request.POST.get('condition', 'near_mint')
            if name:
                card, _ = Card.objects.get_or_create(
                    name=name, set_name=set_name,
                    defaults={'rarity': rarity}
                )
                CollectionCard.objects.get_or_create(
                    user=profile, card=card,
                    defaults={'condition': condition}
                )

        # Remove a card from the collection entirely
        elif action == 'remove_card':
            collection_id = request.POST.get('collection_id')
            CollectionCard.objects.filter(pk=collection_id, user=profile).delete()

        # Decrement quantity, remove if it hits zero
        elif action == 'decrement_card':
            collection_id = request.POST.get('collection_id')
            obj = get_object_or_404(CollectionCard, pk=collection_id, user=profile)
            if obj.quantity > 1:
                obj.quantity -= 1
                obj.save()
            else:
                obj.delete()

        # Create a public listing for a card in the collection
        elif action == 'list_card':
            collection_id = request.POST.get('collection_id')
            caption = request.POST.get('caption', '')
            obj = get_object_or_404(CollectionCard, pk=collection_id, user=profile)
            Listing.objects.get_or_create(
                user=profile, card=obj.card,
                defaults={'condition': obj.condition, 'caption': caption}
            )

        # Remove the public listing for a card (keeps it in collection)
        elif action == 'unlist_card':
            collection_id = request.POST.get('collection_id')
            obj = get_object_or_404(CollectionCard, pk=collection_id, user=profile)
            Listing.objects.filter(user=profile, card=obj.card).delete()

        return redirect('collection')

    # --- GET: build page context ---
    collection = CollectionCard.objects.filter(user=profile).select_related('card').order_by('card__name')
    all_cards = Card.objects.all().order_by('name')
    condition_choices = CollectionCard.CONDITION_CHOICES

    return render(request, 'TradingCG/collection.html', {
        'collection': collection,
        'all_cards': all_cards,
        'condition_choices': condition_choices,
        'profile': profile,
    })


# ---------------------------------------------------------------------------
# Trade request views
# ---------------------------------------------------------------------------

class TradeRequestDetailView(DetailView):
    model = TradeRequest
    template_name = 'TradingCG/show_trade.html'
    context_object_name = 'trade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trade = self.get_object()
        if trade.status == 'accepted':
            context['show_contact'] = True
            context['listing_user'] = trade.listing.user
            context['requester'] = trade.requester
        return context


@login_required(login_url='/TradingCG/login/')
def create_trade_view(request, listing_pk):
    '''
    Create a trade request for a specific listing.
    The listing is passed via URL. The user selects which card from their
    collection they are offering in exchange.
    Prevents users from requesting their own listings.
    '''
    profile = get_profile(request)
    listing = get_object_or_404(Listing, pk=listing_pk)

    if listing.user == profile:
        return redirect('listing', pk=listing_pk)

    collection = CollectionCard.objects.filter(user=profile).select_related('card')

    already_requested = TradeRequest.objects.filter(
        requester=profile, listing=listing
    ).exclude(status='cancelled').exists()

    if request.method == 'POST':
        if already_requested:
            return redirect('listing', pk=listing_pk)

        offered_card_id = request.POST.get('offered_card')
        offered_card = None
        if offered_card_id:
            offered_card = get_object_or_404(CollectionCard, pk=offered_card_id, user=profile)

        trade = TradeRequest.objects.create(
            requester=profile,
            listing=listing,
            offered_card=offered_card,
            status='pending',
        )
        return redirect('show_trade', pk=trade.pk)

    return render(request, 'TradingCG/create_trade.html', {
        'listing': listing,
        'collection': collection,
        'already_requested': already_requested,
        'profile': profile,
    })


@login_required(login_url='/TradingCG/login/')
def cancel_trade_view(request, pk):
    '''
    Allow the requester to cancel a pending trade request they sent.
    Only the requester can cancel, and only if status is pending.
    '''
    profile = get_profile(request)
    trade = get_object_or_404(TradeRequest, pk=pk, requester=profile)

    if trade.status == 'pending':
        trade.status = 'cancelled'
        trade.save()

    return redirect('show_user', pk=profile.pk)


class UpdateTradeRequestView(LoginRequiredMixin, UpdateView):
    """Only the listing owner can accept/decline a trade."""
    model = TradeRequest
    template_name = 'TradingCG/update_trade.html'
    fields = ['status']
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        """Block anyone who is not the listing owner."""
        trade = self.get_object()

        if request.user.profile != trade.listing.user:
            return redirect('show_trade', pk=trade.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('show_trade', kwargs={'pk': self.object.pk})