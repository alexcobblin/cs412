from django.db import models

# Create your models here.
class Joke(models.Model):
    '''Encapsulate the idea of an Joke.'''
 
 
    # data attributes of a Article:
    text = models.TextField(blank=False)
    contributor = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.text[:50]} by {self.contributor}'
    
class Picture(models.Model):
    '''Encapsulate the idea of an Joke.'''
 
 
    # data attributes of a Article:
    contributor = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    url = models.TextField(blank=False)

    
    def __str__(self):
        return f'{self.url} by {self.contributor}'