from django.contrib.auth import get_user_model
from user_data.models import Account, Profile
from swash_service.models import Category, Service, PeriodTime
from swash_order.models import Order, OrderStatus, OrderAddress, OrderMessage
from rest_framework import serializers, status
from user_data.models import Profile


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
            'profile_pic_url',
            'mobile_number',
            'mobile_verified',
            'phone_number',
            'postal_code',
            'sex',
            'age'
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
    profile = serializers.SerializerMethodField()

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
            'services',
            'profile'
        )

    def get_pick_up_address(self, obj):
        try:
            order_pickup_address = OrderAddress.objects.get(order=obj, status='pickup')
            serializer = OrderAddressSerializer(order_pickup_address)

            return serializer.data

        except Exception as e:
            return {}

    def get_delivery_address(self, obj):
        try:
            order = Order.objects.get(user=obj.user, id=obj.id)
            order_pickup_address = OrderAddress.objects.get(order=order, status='delivery')
            serializer = OrderAddressSerializer(order_pickup_address)

            return serializer.data

        except Exception as e:
            return {}

    def get_services(self, obj):
        try:
            order = Order.objects.get(
                user=obj.user,
                id=obj.id
            )
            lst_service = []

            for order_service in order.services.all():
                service = Service.objects.get(id=order_service.service.id)
                service_serializer = ServiceSerializer(service)
                result = service_serializer.data

                result['order_count'] = order_service.count
                lst_service.append(result)

            return lst_service

        except Exception as e:
            return []

    def get_profile(self, obj):
        try:
            order_pickup_address = Profile.objects.get(user=obj.user)
            serializer = ProfileSerializer(order_pickup_address)

            return serializer.data

        except Exception as e:
            return {}


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress

        fields = (
            'lat',
            'long',
            'address',
            'start_time',
            'end_time',
            'selected_date',
            'status'
        )


class PeriodTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodTime

        fields = (
            'id',
            'start_time',
            'end_time'
        )


class OrderMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMessage

        fields = (
            'sender',
            'order',
            'text_message',
            'created_date'
        )
