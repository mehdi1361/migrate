import uuid
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from pip._internal.download import user_agent
from rest_framework import viewsets, status, filters, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .serializers import UserSerializer, AccountSerializer, ProfileSerializer, CategorySerializer, \
    ServiceSerializer, OrderSerializer, PeriodTimeSerializer
from user_data.models import Device, Account, Profile
from swash_service.models import Category, Service, PeriodTime
from swash_order.models import Order, OrderService, OrderStatus, OrderAddress


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
            account = Account.objects.filter(
                account_type=request.data.get('account_type'),
                account_id=request.data.get('account_id')
            )

            if account.count() == 0:
                account = Account.objects.create(
                    user=request.user,
                    account_type=request.data.get('account_type'),
                    account_id=request.data.get('account_id')
                )

                serializer = self.serializer_class(account)

            elif account.count() == 1:
                serializer = self.serializer_class(account[0])

            else:
                raise Exception('multi user set account')

            return Response(
                {
                    'id': 200,
                    'data': serializer.data,
                    'message': 'account set for device'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    'id': 400,
                    'data': '-100',
                    'message': 'error in params'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    # @list_route(methods=['post'])
    def create(self, request):
        if request.user.accounts.count() <= 0:
            return Response(
                {
                    'id': 400,
                    'data': -100,
                    'message': 'no account registered'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if request.user
        return Response(
            {
                'id': 200,
                'data': request.user.username,
                'message': 'profile registered'
            },
            status=status.HTTP_200_OK
        )


class CategoryViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @list_route(methods=['post'])
    def main(self, request):
        categories = Category.objects.filter(parent=None)
        serializer = self.serializer_class(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def sub(self, request):
        try:
            category_id = request.data.get('category_id')
            parent = get_object_or_404(Category, pk=category_id)
            categories = Category.objects.filter(parent=parent)
            serializer = self.serializer_class(categories, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'id': 400, 'message': e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def service(self, request):
        try:
            category_id = request.data.get('category_id')
            category = get_object_or_404(Category, pk=category_id)
            services = Service.objects.filter(category=category)
            serializer = ServiceSerializer(services, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': e}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @list_route(methods=['post'])
    def bag(self, request):
        try:
            order = Order.objects.get(user=request.user, status__in=('draft', 'pickup'))
            serializer = self.serializer_class(order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def add(self, request):
        try:
            service_id = request.data.get('service_id')
            service = get_object_or_404(Service, pk=service_id)

            order, created = Order.objects.get_or_create(
                user=request.user,
                defaults={'status': 'draft'}
            )

            if created:
                OrderService.objects.create(order=order, service=service)
                OrderStatus.objects.create(order=order, status='draft')

            else:
                try:
                    order_service = OrderService.objects.get(order=order, service=service)

                    order_service.count += 1
                    order_service.save()

                except Exception as e:
                    OrderService.objects.create(order=order, service=service)

            serializer = self.serializer_class(order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def sub(self, request):
        try:
            service_id = request.data.get('service_id')
            service = get_object_or_404(Service, pk=service_id)
            order = get_object_or_404(Order, user=request.user, status='draft')
            order_service = get_object_or_404(OrderService, service=service, order=order)

            order_service.count -= 1
            order_service.save()

            if order_service.count <= 0:
                order_service.delete()

            serializer = self.serializer_class(order)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def confirm(self, request):
        order = get_object_or_404(Order, user=request.user, defaults={'status': 'pickup'})
        order.status = 'confirmed'
        order.save()

        OrderStatus.objects.create(order=order, status='confirmed')

        return Response({"id": 200, "message": "order confirmed"}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def address(self, request):
        try:
            lat = request.data.get('lat')
            long = request.data.get('long')
            address = request.data.get('address')
            state = request.data.get('status')
            period_time = request.data.get('period_time')
            date_pickup = request.data.get('period_time')

            if lat is None:
                raise Exception('lat cant null')

            if long is None:
                raise Exception('long cant null')

            if address is None:
                raise Exception('address cant null')

            if state is None or state not in ('pickup', 'delivery', 'alternative'):
                raise Exception('state not valid')

            if period_time is None:
                raise Exception('period_time not valid')

            if date_pickup is None:
                raise Exception('date pickup not valid')

            order = Order.objects.get(user=request.user, status__in=('draft', 'pickup'))
            period_time_entity = get_object_or_404(PeriodTime, id=period_time)
            order.start_time = period_time_entity.start_time
            order.end_time = period_time_entity.end_time
            order.pickup_date = date_pickup

            try:
                order_address = OrderAddress.objects.get(order=order, status=status)
                order_address.address = address
                order_address.lat = lat
                order_address.long = long
                order_address.save()

            except:
                OrderAddress.objects.create(
                    order=order,
                    lat=lat,
                    long=long,
                    address=address,
                    status=state
                )
            OrderStatus.objects.create(order=order, status='pickup')
            order.status = 'pickup'
            order.save()

            serializer = self.serializer_class(order)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def pend_or_cancel(self, request):
        try:
            state = request.data.get('state')
            order = Order.objects.filter(user=request.user).exclude(status__in=('pending', 'cancel'))

            if order.count() == 0 or order.count() >= 2:
                raise Exception('order not valid')

            if state is None or state not in ('pending', 'cancel'):
                raise Exception('state not valid')

            selected_order = order[0]
            selected_order.status = state
            selected_order.save()

            serializer = self.serializer_class(selected_order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def paid(self, request):
        order = get_object_or_404(Order, user=request.user, status='pickup')
        order.status = 'paid'
        order.save()
        serializer = self.serializer_class(order)

        return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def confirm(self, request):
        order = get_object_or_404(Order, user=request.user, status='paid')
        order.status = 'confirmed'
        order.save()

        serializer = self.serializer_class(order)

        return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def order_list(self, request):
        orders = Order.objects.filter(status='confirmed')
        serializer = OrderSerializer(orders, many=True)
        return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)


class PeriodViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = PeriodTime.objects.all()
    serializer_class = PeriodTimeSerializer
