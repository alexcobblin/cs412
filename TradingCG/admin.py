from django.contrib import admin

# Register your models here.
from .models import User
from .models import Card
from .models import Listing
from .models import Photo
from .models import TradeRequest

admin.site.register(User)
admin.site.register(Card)
admin.site.register(Photo)
admin.site.register(Listing)
admin.site.register(TradeRequest)