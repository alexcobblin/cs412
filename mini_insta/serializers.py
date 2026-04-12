from rest_framework import serializers
from .models import Article, Profile, Post, Photo, Follow, Comment, Like
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'author', 'text', 'published', 'image_url']


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'post', 'image', 'timestamp']

    def get_image(self, obj):
        return obj.get_image_url()


class CommentSerializer(serializers.ModelSerializer):
    profile_display_name = serializers.CharField(
        source='profile.display_name', read_only=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'profile', 'profile_display_name', 'text', 'timestamp']


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(source='get_all_photos', many=True, read_only=True)
    comments = CommentSerializer(source='get_all_comments', many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    profile_display_name = serializers.CharField(
        source='profile.display_name', read_only=True
    )

    class Meta:
        model = Post
        fields = [
            'id', 'profile', 'profile_display_name',
            'caption', 'timestamp', 'photos', 'comments', 'likes_count'
        ]

    def get_likes_count(self, obj):
        return obj.get_likes().count()


class ProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(source='get_all_posts', many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'display_name', 'bio_text',
            'join_date', 'profile_image_url',
            'followers_count', 'following_count', 'posts'
        ]

    def get_followers_count(self, obj):
        return obj.get_num_followers()

    def get_following_count(self, obj):
        return obj.get_num_following()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'profile', 'follower_profile', 'timestamp']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email')
        )
        return user
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption']