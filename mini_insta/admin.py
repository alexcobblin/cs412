from django.contrib import admin

# Register your models here.
from .models import Article
from .models import Profile
from .models import Post
from .models import Photo
from .models import Follow
from .models import Comment
from .models import Like

admin.site.register(Profile)
admin.site.register(Article)

admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)