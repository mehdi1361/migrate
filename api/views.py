import uuid
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .serializers import UserSerializer, AccountSerializer
from user_data.models import Device, Account


class DefaultsMixin(object):
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class AuthMixin(object):
    authentication_classes = (
        TokenAuthentication,
        JSONWebTokenAuthentication
    )

    permission_classes = (
        IsAuthenticated,
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (AllowAny,)

        return super(UserViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        device_id = request.data['deviceUniqueID']
        device_name = request.data['deviceName']
        return_id = 200
        try:
            device = Device.objects.get(device_id=device_id)
            user_id = device.user.user.username

        except Exception:

            user_id = str(uuid.uuid1().int >> 32)
            user = User.objects.create_user(username=user_id, password=user_id)
            Device.objects.create(device_model=device_name, device_id=device_id, user=user)
            return_id = 201

        finally:
            return Response(
                {'id': return_id, 'user_id': user_id},
                status=status.HTTP_201_CREATED if return_id == 201 else status.HTTP_200_OK
            )


class AccountViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @list_route(methods=['post'])
    def set_account(self, request):
        try:
            account = Account.objects.get(
                user=request.user,
                account_type=request.data.get('account_type'),
                account_id=request.data.get('account_id')
            )

            return Response(
                {'id': 400, 'user_id': '-100'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Account.DoesNotExist:
            account = Account.objects.create(
                user=request.user,
                account_type=request.data.get('account_type'),
                account_id=request.data.get('account_id')
            )

            serializer = self.serializer_class(account)

            return Response(
                {'id': 200, 'data': serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'id': 400, 'user_id': '-100'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @list_route(methods=['post'])
    def get_account(self, request):
        try:
            account = Account.objects.get(
                user=request.user,
                account_type=request.data.get('account_type'),
                account_id=request.data.get('account_id')
            )

            return Response(
                {'id': 200, 'user_id': account.user.username},
                status=status.HTTP_200_OK
            )

        except Account.DoesNotExist:
            return Response(
                {'id': 404, 'user_id': None},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {'id': 400, 'user_id': '-100'},
                status=status.HTTP_400_BAD_REQUEST
            )
