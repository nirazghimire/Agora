from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product

#this is basically a translator 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'