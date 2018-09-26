from django.contrib.auth import get_user_model
from user_data.models import Account, Profile
from swash_service.models import Category, Service
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account

        fields = (
            'id',
            'account_type',
            'account_id'
        )


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile

        fields = (
            'first_name',
            'last_name',
            'gender',
            'email'
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

        fields = (
            'name',
            'icon',
            'details',
            'discount',
            'notification',
            'parent'
        )


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service

        fields = (
            'name',
            'icon',
            'notification',
            'details',
            'price',
            'discount',
            'duration',
            'category'
        )