from django.contrib import admin

# Register your models here.
# Register your models here.
from .models import Article
from .models import Profile

admin.site.register(Profile)
admin.site.register(Article)