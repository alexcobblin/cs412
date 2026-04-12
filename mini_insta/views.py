# mini_insta/views.py
# views for the mini_insta application

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from .models import Article, Profile, Post, Photo, Follow, Comment, Like
from .forms import CreatePostForm, UpdateProfileForm, UpdatePostForm
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            # Find the linked Profile by matching username
            try:
                profile = Profile.objects.get(username=user.username)
                profile_id = profile.pk
            except Profile.DoesNotExist:
                profile_id = None
            return Response({
                'token': token.key,
                'profile_id': profile_id,
            }, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid Credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ShowAllView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''

    model = Article
    template_name = 'mini_insta/show_all.html'
    context_object_name = 'articles'


class ArticleView(DetailView):
    '''Show the details for one article.'''

    model = Article
    template_name = 'mini_insta/article.html'
    context_object_name = 'article'


class RandomArticleView(DetailView):
    '''Show the details for one article.'''

    model = Article
    template_name = 'mini_insta/article.html'
    context_object_name = 'article'

    def get_object(self):
        '''Return one Article object chosen at random.'''

        all_articles = Article.objects.all()
        return random.choice(all_articles)


class ProfileListView(ListView):
    '''Show all profiles.'''

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'

class ProfileView(DetailView):
    '''Show the details for one profile.'''

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

class PostDetailView(DetailView):
    '''Show the details for one post, including all its photos, comments, and likes.'''

    model = Post
    template_name = 'mini_insta/show_post.html'
    context_object_name = 'post'

class CreatePostView(CreateView):

    form_class = CreatePostForm
    template_name = 'mini_insta/create_post_form.html'

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''This method handles the form submission and saves the
        new object to the Django database.
        We need to add the foreign key (of the Profile) to the Post
        object before saving it to the database.
        '''

        print(f'CreatePostView.form_valid: form.cleaned_data={form.cleaned_data}')

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        post = form.save()

        files = self.request.FILES.getlist('files')
        for f in files:
            photo = Photo(post=post, image_file=f)
            photo.save()
            print(f'CreatePostView.form_valid: saved photo={photo}')
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new Post.'''

        return reverse('post', kwargs={'pk': self.object.pk})


class UpdateProfileView(UpdateView):
    '''A view to update a Profile and save it to the database.'''

    form_class = UpdateProfileForm
    template_name = 'mini_insta/update_profile_form.html'
    model = Profile

    def form_valid(self, form):
        '''Handle the form submission to update a Profile object.'''

        print(f'UpdateProfileView: form.cleaned_data={form.cleaned_data}')
        return super().form_valid(form)


class UpdatePostView(UpdateView):
    '''A view to update a Post and save it to the database.'''

    form_class = UpdatePostForm
    template_name = 'mini_insta/update_post_form.html'
    model = Post

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['profile'] = self.get_object().profile
        return context

    def form_valid(self, form):
        '''Handle the form submission to update a Post object.'''

        print(f'UpdatePostView: form.cleaned_data={form.cleaned_data}')
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after updating a Post.'''

        return reverse('post', kwargs={'pk': self.object.pk})


class DeletePostView(DeleteView):
    '''A view to delete a Post and remove it from the database.'''

    template_name = 'mini_insta/delete_post_form.html'
    model = Post
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)

        context['post'] = post
        context['profile'] = post.profile
        return context

    def get_success_url(self):
        '''Return the URL to which we should be directed after the delete.'''

        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        profile = post.profile

        return reverse('profile', kwargs={'pk': profile.pk})

class ShowFollowersDetailView(DetailView):
    '''Show the followers for one profile.'''

    model = Profile
    template_name = 'mini_insta/show_followers.html'
    context_object_name = 'profile'

class ShowFollowingDetailView(DetailView):
    '''Show the profiles being followed by one profile.'''

    model = Profile
    template_name = 'mini_insta/show_following.html'
    context_object_name = 'profile'

class PostFeedListView(ListView):
    '''Show the post feed for one profile.'''

    model = Post
    template_name = 'mini_insta/show_feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        '''Return the QuerySet of Posts for this profile's feed.'''

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['profile'] = Profile.objects.get(pk=pk)
        return context

class SearchView(ListView):
    '''A view to search Profiles and Posts.'''

    template_name = 'mini_insta/search_results.html'
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        '''Dispatch the request; show search form if no query provided.'''

        if 'query' not in request.GET:
            pk = self.kwargs['pk']
            profile = Profile.objects.get(pk=pk)
            return render(request, 'mini_insta/search.html', {'profile': profile})

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        '''Return Posts that match the search query.'''

        query = self.request.GET.get('query', '')
        posts = Post.objects.filter(caption__icontains=query).order_by('-timestamp')
        return posts

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile

        query = self.request.GET.get('query', '')
        context['query'] = query
        context['posts'] = Post.objects.filter(caption__icontains=query).order_by('-timestamp')
        context['profiles'] = Profile.objects.filter(
            username__icontains=query
        ) | Profile.objects.filter(
            display_name__icontains=query
        ) | Profile.objects.filter(
            bio_text__icontains=query
        )

        return context
    
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer, PostSerializer, ProfileSerializer, FollowSerializer, PhotoSerializer

class ShowAllAPIView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''

    model = Article
    template_name = 'mini_insta/show_all.html'
    context_object_name = 'articles'


class ArticleAPIView(DetailView):
    '''Show the details for one article.'''

    model = Article
    template_name = 'mini_insta/article.html'
    context_object_name = 'article'


class RandomArticleAPIView(DetailView):
    '''Show the details for one article.'''

    model = Article
    template_name = 'mini_insta/article.html'
    context_object_name = 'article'

    def get_object(self):
        '''Return one Article object chosen at random.'''

        all_articles = Article.objects.all()
        return random.choice(all_articles)


class ProfileListAPIView(ListView):
    '''Show all profiles.'''

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'

class ProfileAPIView(DetailView):
    '''Show the details for one profile.'''

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

class PostDetailAPIView(DetailView):
    '''Show the details for one post, including all its photos, comments, and likes.'''

    model = Post
    template_name = 'mini_insta/show_post.html'
    context_object_name = 'post'

class CreatePostAPIView(CreateView):

    form_class = CreatePostForm
    template_name = 'mini_insta/create_post_form.html'

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''This method handles the form submission and saves the
        new object to the Django database.
        We need to add the foreign key (of the Profile) to the Post
        object before saving it to the database.
        '''

        print(f'CreatePostView.form_valid: form.cleaned_data={form.cleaned_data}')

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        post = form.save()

        files = self.request.FILES.getlist('files')
        for f in files:
            photo = Photo(post=post, image_file=f)
            photo.save()
            print(f'CreatePostView.form_valid: saved photo={photo}')
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new Post.'''

        return reverse('post', kwargs={'pk': self.object.pk})


class UpdateProfileAPIView(UpdateView):
    '''A view to update a Profile and save it to the database.'''

    form_class = UpdateProfileForm
    template_name = 'mini_insta/update_profile_form.html'
    model = Profile

    def form_valid(self, form):
        '''Handle the form submission to update a Profile object.'''

        print(f'UpdateProfileView: form.cleaned_data={form.cleaned_data}')
        return super().form_valid(form)


class UpdatePostAPIView(UpdateView):
    '''A view to update a Post and save it to the database.'''

    form_class = UpdatePostForm
    template_name = 'mini_insta/update_post_form.html'
    model = Post

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['profile'] = self.get_object().profile
        return context

    def form_valid(self, form):
        '''Handle the form submission to update a Post object.'''

        print(f'UpdatePostView: form.cleaned_data={form.cleaned_data}')
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after updating a Post.'''

        return reverse('post', kwargs={'pk': self.object.pk})


class DeletePostAPIView(DeleteView):
    '''A view to delete a Post and remove it from the database.'''

    template_name = 'mini_insta/delete_post_form.html'
    model = Post
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)

        context['post'] = post
        context['profile'] = post.profile
        return context

    def get_success_url(self):
        '''Return the URL to which we should be directed after the delete.'''

        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        profile = post.profile

        return reverse('profile', kwargs={'pk': profile.pk})

class ShowFollowersDetailAPIView(DetailView):
    '''Show the followers for one profile.'''

    model = Profile
    template_name = 'mini_insta/show_followers.html'
    context_object_name = 'profile'

class ShowFollowingDetailAPIView(DetailView):
    '''Show the profiles being followed by one profile.'''

    model = Profile
    template_name = 'mini_insta/show_following.html'
    context_object_name = 'profile'

class PostFeedListAPIView(ListView):
    '''Show the post feed for one profile.'''

    model = Post
    template_name = 'mini_insta/show_feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        '''Return the QuerySet of Posts for this profile's feed.'''

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['profile'] = Profile.objects.get(pk=pk)
        return context

class SearchAPIView(ListView):
    '''A view to search Profiles and Posts.'''

    template_name = 'mini_insta/search_results.html'
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        '''Dispatch the request; show search form if no query provided.'''

        if 'query' not in request.GET:
            pk = self.kwargs['pk']
            profile = Profile.objects.get(pk=pk)
            return render(request, 'mini_insta/search.html', {'profile': profile})

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        '''Return Posts that match the search query.'''

        query = self.request.GET.get('query', '')
        posts = Post.objects.filter(caption__icontains=query).order_by('-timestamp')
        return posts

    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template.'''

        context = super().get_context_data(**kwargs)

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile

        query = self.request.GET.get('query', '')
        context['query'] = query
        context['posts'] = Post.objects.filter(caption__icontains=query).order_by('-timestamp')
        context['profiles'] = Profile.objects.filter(
            username__icontains=query
        ) | Profile.objects.filter(
            display_name__icontains=query
        ) | Profile.objects.filter(
            bio_text__icontains=query
        )

        return context

class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProfilePostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        return profile.get_all_posts()

class ProfileFeedAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        return profile.get_post_feed()

class CreatePostAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(profile=profile)
            files = request.FILES.getlist('files')
            for f in files:
                Photo.objects.create(post=post, image_file=f)
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)