from rest_framework import serializers
from .models import Joke, Picture

class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ['id', 'text', 'contributor', 'published']

    def create(self, validated_data):
        print(f'JokeSerializer.create, validated_data={validated_data}')
        return Joke.objects.create(**validated_data)

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['id', 'url', 'contributor', 'published']