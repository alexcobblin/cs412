# file: quotes/views.py

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
 
 
import time
 
 
def home(request):
    '''
    Define a view to handle the 'home' request.
    '''
 
 
    response_text = f'''
    <html>
    <h1>Hello, world!</h1>
 
 
    The current time is {time.ctime()}.
    </html>
    '''
 
 
    return HttpResponse(response_text)