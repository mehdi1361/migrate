from django.contrib.auth import get_user_model
from user_data.models import Account, Profile
from swash_service.models import Category, Service
from swash_order.models import Order, OrderStatus, OrderAddress
from rest_framework import serializers, status


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
        try:
            order = Order.objects.get(user=requests.user, status='pickup')
            order_pickup_address = OrderAddress.objects.get(order=order, status='pickup')
            serializer = OrderAddressSerializer(order_pickup_address)

            return serializer.data

        except Exception as e:
            return {}

    def get_delivery_address(self, requests):
        try:
            order = Order.objects.get(user=requests.user, status='pickup')
            order_pickup_address = OrderAddress.objects.get(order=order, status='delivery')
            serializer = OrderAddressSerializer(order_pickup_address)

            return serializer.data

        except Exception as e:
            return {}

    def get_services(self, requests):
        order = Order.objects.get(
            user=requests.user,
            status__in=('draft', 'pending', 'pickup')
        )
        lst_service = []

        for order_service in order.services.all():
            service = Service.objects.get(id=order_service.service.id)
            service_serializer = ServiceSerializer(service)
            result = service_serializer.data

            result['order_count'] = order_service.count
            lst_service.append(result)

        return lst_service


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress

        fields = (
            'lat',
            'long',
            'address',
            'status'
        )
