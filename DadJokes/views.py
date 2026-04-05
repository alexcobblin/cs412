from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from .models import Joke, Picture  # correct relative import
import random

class JokeView(DetailView):
    '''Show one joke by primary key.'''
    model = Joke
    template_name = 'dadjokes/joke.html'
    context_object_name = 'joke'

class PictureView(DetailView):
    '''Show one picture by primary key.'''
    model = Picture
    template_name = 'dadjokes/picture.html'
    context_object_name = 'picture'

class JokeListView(ListView):
    '''Show all jokes.'''
    model = Joke
    template_name = 'dadjokes/jokes.html'
    context_object_name = 'jokes'

class PictureListView(ListView):
    '''Show all pictures.'''
    model = Picture
    template_name = 'dadjokes/pictures.html'
    context_object_name = 'pictures'

class RandomView(View):
    '''Show one random joke and one random picture.'''
    template_name = 'dadjokes/random.html'

    def get(self, request, *args, **kwargs):
        jokes = Joke.objects.all()
        pictures = Picture.objects.all()
        context = {
            'joke': random.choice(list(jokes)),
            'picture': random.choice(list(pictures)),
        }
        return render(request, self.template_name, context)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import JokeSerializer, PictureSerializer

class JokeListAPIView(generics.ListCreateAPIView):
    '''GET all jokes, POST a new joke.'''
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer

class JokeDetailAPIView(generics.RetrieveAPIView):
    '''GET one joke by pk.'''
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer

class RandomJokeAPIView(APIView):
    '''GET one random joke.'''
    def get(self, request):
        joke = random.choice(list(Joke.objects.all()))
        serializer = JokeSerializer(joke)
        return Response(serializer.data)

class PictureListAPIView(generics.ListAPIView):
    '''GET all pictures.'''
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

class PictureDetailAPIView(generics.RetrieveAPIView):
    '''GET one picture by pk.'''
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

class RandomPictureAPIView(APIView):
    '''GET one random picture.'''
    def get(self, request):
        picture = random.choice(list(Picture.objects.all()))
        serializer = PictureSerializer(picture)
        return Response(serializer.data)