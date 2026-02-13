# blog/views.py
# Define the views for the blog app:
 
 
#from django.shortcuts import render
from .models import Article, Profile
from django.views.generic import ListView, DetailView
import random
 
 
class ShowAllView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''
 
 
    model = Article # retrieve objects of type Article from the database
    template_name = 'mini_insta/show_all.html'
    context_object_name = 'articles'

class ArticleView(DetailView):
    '''Show the details for one article.'''
    model = Article
    template_name = 'mini_insta/article.html' ## reusing same template!!
    context_object_name = 'article'

class RandomArticleView(DetailView):
    '''Show the details for one article.'''
    model = Article
    template_name = 'mini_insta/article.html'
    context_object_name = 'article'
 
 
    # pick one article at random:
    def get_object(self):
        '''Return one Article object chosen at random.'''
 
 
        all_articles = Article.objects.all()
        return random.choice(all_articles)
class ProfileListView(ListView):
    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'
class ProfileView(DetailView):
    model = Profile
    template_name = 'mini_insta/show_profile.html' ## reusing same template!!
    context_object_name = 'profile'