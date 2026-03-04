from django.db import models
from django.urls import reverse

class Article(models.Model):
    '''Encapsulate the idea of an Article by some author.'''
 
 
    # data attributes of a Article:
    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True)
    
    def __str__(self):
        '''Return a string representation of this Article object.'''
        return f'{self.title} by {self.author}'

class Profile(models.Model):
    '''Encapsulate the idea of a user Profile.'''

    username = models.TextField(blank=False)
    display_name = models.TextField(blank=False)
    bio_text = models.TextField(blank=False)
    join_date = models.DateTimeField(auto_now=True)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        '''Return a string representation of this Profile object.'''
        return f'{self.display_name} by {self.username}'

    def get_absolute_url(self):
        '''Return the URL to display one instance of this model.'''
        return reverse('profile', kwargs={'pk': self.pk})

    def get_all_posts(self):
        '''Return all of the posts for this profile.'''
        posts = Post.objects.filter(profile=self).order_by('-timestamp')
        return posts

    def get_followers(self):
        '''Return a list of Profiles who follow this profile.'''
        follows = Follow.objects.filter(profile=self)
        return [f.follower_profile for f in follows]

    def get_num_followers(self):
        '''Return the count of followers for this profile.'''
        return len(self.get_followers())

    def get_following(self):
        '''Return a list of Profiles that this profile is following.'''
        follows = Follow.objects.filter(follower_profile=self)
        return [f.profile for f in follows]

    def get_num_following(self):
        '''Return the count of profiles being followed.'''
        return len(self.get_following())

    def get_post_feed(self):
        '''Return all Posts from Profiles that this profile is following, newest first.'''
        following = self.get_following()
        posts = Post.objects.filter(profile__in=following).order_by('-timestamp')
        return posts


class Post(models.Model):
    '''Encapsulate the idea of a Post by a Profile.'''

    # data attributes of a Post:
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def __str__(self):
        '''Return a string representation of this Post object.'''
        return f'Post by {self.profile.display_name} at {self.timestamp}'

    def get_absolute_url(self):
        '''Return the URL to display one instance of this model.'''
        return reverse('post', kwargs={'pk': self.pk})

    def get_all_photos(self):
        '''Return all of the photos for this post.'''
        photos = Photo.objects.filter(post=self).order_by('timestamp')
        return photos

    def get_all_comments(self):
        '''Return all of the comments for this post.'''
        comments = Comment.objects.filter(post=self).order_by('timestamp')
        return comments

    def get_likes(self):
        '''Return all of the likes for this post.'''
        likes = Like.objects.filter(post=self)
        return likes


class Photo(models.Model):
    '''Encapsulate the idea of a Photo associated with a Post.'''

    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    image_url = models.URLField(blank=True)     # kept for backwards-compatibility
    image_file = models.ImageField(blank=True)  # new: actual uploaded image file
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string representation of this Photo object.'''
        if self.image_file:
            return f'Photo (file) for Post {self.post.pk} at {self.timestamp}'
        return f'Photo (url) for Post {self.post.pk} at {self.timestamp}'

    def get_image_url(self):
        '''Return the URL to the image, whether stored as a file or a URL.'''
        if self.image_file:
            return self.image_file.url
        return self.image_url


class Follow(models.Model):
    '''Encapsulate one Profile following another Profile.'''

    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="profile"
    )
    follower_profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="follower_profile"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string representation of this Follow object.'''
        return f'{self.follower_profile.display_name} follows {self.profile.display_name}'


class Comment(models.Model):
    '''Encapsulate a Comment on a Post.'''

    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=False)

    def __str__(self):
        '''Return a string representation of this Comment object.'''
        return f'Comment by {self.profile.display_name} on Post {self.post.pk}: {self.text[:50]}'


class Like(models.Model):
    '''Encapsulate the idea of a Like on a Post.'''

    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return a string representation of this Like object.'''
        return f'Like by {self.profile.display_name} on Post {self.post.pk}'