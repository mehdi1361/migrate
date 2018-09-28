from django.contrib.auth import get_user_model
from user_data.models import Account, Profile
from swash_service.models import Category, Service
from swash_order.models import Order, OrderService, OrderStatus
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
            'id',
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
            'id',
            'name',
            'icon',
            'notification',
            'details',
            'price',
            'discount',
            'duration',
            'category'
        )


class OrderSerializer(serializers.ModelSerializer):
    pick_up_address = serializers.SerializerMethodField()
    delivery_address = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = (
            'id',
            'status',
            'price',
            'discount',
            'pure',
            'pick_up_address',
            'delivery_address',
            'services'
        )

    def get_pick_up_address(self, requests):
        return None

    def get_delivery_address(self, requests):
        return None

    def get_services(self, requests):
        return None
