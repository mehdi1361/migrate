from django.contrib.auth import get_user_model
from user_data.models import Account
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
