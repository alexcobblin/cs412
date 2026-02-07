from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random
 
 
# Create your views here.

quotes = [ 
    "I'm Batman.",
    "You either die a hero, or you live long enough to see yourself become the villain.",
    "It's not who I am underneath, but what I do that defines me.",
    "I'm whatever Gotham needs me to be.",
    "I will become the consequence.",
    "A hero can be anyone.",
    "I'm not wearing hockey pads.",
    "I never thought I'd feel fear like that. I thought I'd mastered all that.",
    "Swear to me!",
    "This city just showed you... that it's full of people ready to believe in good.",
    "I made you, you made me first.",
    "I use the night, I became the night, sooner or later I'll go down.",
]

images = [
    "quotes/images/batman1.jpg",
    "quotes/images/batman2.jpg",
    "quotes/images/batman3.jpg",
]
 
 
def quote(request):
    '''
    Display one random quote and image.
    '''
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    
    context = {
        'quote': selected_quote,
        'image': selected_image,
    }
    
    return render(request, 'quotes/quote.html', context)


def show_all(request):
    '''
    Display all quotes and images.
    '''
    context = {
        'quotes': quotes,
        'images': images,
    }
    
    return render(request, 'quotes/show_all.html', context)


def about(request):
    '''
    Display information about Batman.
    '''
    return render(request, 'quotes/about.html')