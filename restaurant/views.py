from django.shortcuts import render
import random
from datetime import datetime, timedelta

# Create your views here.

def main(request):
    '''Show the main page.'''
    
    template_name = "restaurant/main.html"
    return render(request, template_name)

def order(request):
    '''Show the order page.'''
    
    template_name = "restaurant/order.html"
    
    specials = ["Hamburgeesa", "Pizzaless Peperoni", "Knuckle Sandwich"]
    daily_special = random.choice(specials)
    
    context = {
        'daily_special': daily_special,
    }
    
    return render(request, template_name, context=context)

def confirmation(request):
    '''Process the form submission and show confirmation.'''
    
    template_name = "restaurant/confirmation.html"
    
    if request.POST:
        
        # Read customer info
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        instructions = request.POST.get('instructions', '')
        
        # Collect ordered items
        items = []
        total = 0
        tax = 0
        
        if 'item1' in request.POST:
            items.append("Bread")
            total += 12.99
            tax += 12.99 * 0.07
            
        if 'item2' in request.POST:
            items.append("Owl Soup")
            total += 9.99
            tax += 9.99 * 0.07
            
        if 'item3' in request.POST:
            items.append("Vegan Owl Soup")
            total += 7.99
            tax += 7.99 * 0.07
            
        if 'daily_special' in request.POST:
            items.append(request.POST['daily_special'])
            total += 14.99
            tax += 20000000000
        
        # Calculate ready time (30-60 minutes from now)
        minutes = random.randint(30, 60)
        ready_time = datetime.now() + timedelta(minutes=minutes)
        ready_time_str = ready_time.strftime("%I:%M %p") + " UK time"
        
        context = {
            'name': name,
            'phone': phone,
            'email': email,
            'tax': f"{tax:.2f}",
            'instructions': instructions,
            'items': items,
            'total': f"{total:.2f}",
            'ready_time': ready_time_str,
            'full_price': f"{total + tax:.2f}",
        }
        
        return render(request, template_name, context=context)
