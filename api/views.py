import random
import uuid
import datetime as main_datetime
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .serializers import UserSerializer, AccountSerializer, ProfileSerializer, CategorySerializer, \
    ServiceSerializer, OrderSerializer, PeriodTimeSerializer, OrderMessageSerializer, TicketSerializer
from user_data.models import Device, Account, Profile, Verification, Ticket, TicketMessage
from swash_service.models import Category, Service, PeriodTime
from swash_order.models import Order, OrderService, OrderStatus, OrderAddress, OrderMessage
from django.db import transaction


def mobile_verified():
    def decorator(drf_custom_method):
        def _decorator(self, *args, **kwargs):
            if Profile.is_active(self.request.user):
                return drf_custom_method(self, *args, **kwargs)
            else:
                return Response({'id': 406, 'message': 'mobile not verified'},
                                status=status.HTTP_406_NOT_ACCEPTABLE
                                )

        return _decorator

    return decorator


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

        if device_id is None:
            return Response({'id': 400, 'message': 'device id not in request'},
                            status=status.HTTP_400_BAD_REQUEST)

        if device_name is None:
            return Response({'id': 400, 'message': 'device name not in request'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            return_id = 200
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
    @mobile_verified()
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

    @list_route(methods=['POST'])
    def set_mobile_number(self, request):
        mobile_no = request.data.get('mobile_no')

        if mobile_no is None:
            return Response({'id': 400, 'message': 'mobile number not found'}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = random.randint(1000, 9999)

        try:
            user_profile = Profile.objects.get(mobile_number=mobile_no)

        except Exception as e:
            user_profile = Profile.objects.get(user=request.user)
            user_profile.mobile_number = mobile_no

        finally:
            user_profile.mobile_verified = False
            user_profile.save()
            # inline = Inline(mobile_nu=mobile_no, message=verification_code)
            # result = inline.run()
            result = True

            if result:
                Verification.objects.create(
                    verification_code=verification_code,
                    profile=user_profile
                )

                return Response({'id': 200, 'message': 'verification code sent!!!'}, status=status.HTTP_200_OK)

        return Response({'id': 400, 'message': 'verification code send failed'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def register(self, request):
        try:
            # file = request.FILES['profile_pic_url']
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            phone_number = request.data.get('phone_number')
            postal_code = request.data.get('postal_code')
            age = request.data.get('age')
            sex = request.data.get('sex')

            if first_name is None:
                raise Exception('first name not found')

            if last_name is None:
                raise Exception('last name not found')

            if phone_number is None:
                raise Exception('phone number not found')

            if postal_code is None:
                raise Exception('postal code not found')

            if sex is None:
                raise Exception('sex not found')

            if age is None:
                raise Exception('age not found')

            try:
                profile = Profile.objects.get(user=request.user)
                raise Exception('profile already exist!!!')

            except:
                profile = Profile.objects.create(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    postal_code=postal_code,
                    age=age,
                    sex=sex
                )
                serializer = self.serializer_class(profile)
                return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def edit(self, request):
            # file = request.FILES['profile_pic_url']
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        phone_number = request.data.get('phone_number')
        postal_code = request.data.get('postal_code')
        age = request.data.get('age')
        sex = request.data.get('sex')

        if first_name is None:
            raise Exception('first name not found')

        if last_name is None:
            raise Exception('last name not found')

        if phone_number is None:
            raise Exception('phone number not found')

        if postal_code is None:
            raise Exception('postal code not found')

        if age is None:
            raise Exception('age not found')

        if sex is None:
            raise Exception('sex not found')

        try:
            profile = Profile.objects.get(user=request.user)
            profile.first_name = first_name
            profile.last_name = last_name
            profile.phone_number = phone_number
            profile.postal_code = postal_code
            profile.age = age
            profile.sex = sex
            profile.save()

        except Exception as e:
            return Response({'id': 400, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def show(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def set_picture(self, request):
        try:
            file = request.FILES['profile_pic_url']

            if file is None:
                raise Exception('file not found')

            profile = Profile.objects.get(user=request.user)
            profile.profile_pic_url = file
            profile.save()

            serializer = ProfileSerializer(profile)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'])
    def verified(self, request):
        try:
            response_id = 400
            state = status.HTTP_400_BAD_REQUEST

            verification_code = request.data.get('verification_code')
            mobile_no = request.data.get('mobile_no')

            if mobile_no is None:
                raise Exception('mobile no not found')

            if verification_code is None:
                raise Exception('verification_code no not found')

            verified, message, user_id = Verification.is_verified(
                mobile_no=mobile_no,
                verification_code=verification_code,
                user=request.user
            )

            if verified:
                profile = Profile.objects.get(user=user_id)
                profile.mobile_verified = True
                profile.save()
                response_id = 200
                state = status.HTTP_200_OK

            return Response({'id': response_id, 'message': message, "user_id": user_id}, status=state)

        except Exception as e:
            return Response({'id': 400, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @list_route(methods=['post'])
    @mobile_verified()
    def main(self, request):
        categories = Category.objects.filter(parent=None)
        serializer = self.serializer_class(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    @mobile_verified()
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
    @mobile_verified()
    def service(self, request):
        try:
            category_id = request.data.get('category_id')
            category = get_object_or_404(Category, pk=category_id)
            services = Service.objects.filter(category=category)
            serializer = ServiceSerializer(services, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def sub_service(self, request):
        try:
            category_id = request.data.get('category_id')
            if category_id is None:
                raise Exception('error in parameter category_id not found')

            parent = Category.objects.get(id=category_id)
            categories = list(Category.objects.filter(parent=parent).values_list('id', flat=True))

            services = Service.objects.filter(category__parent_id__in=categories)
            serializer = ServiceSerializer(services, many=True)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'id': 400, 'message': e}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @list_route(methods=['post'])
    @mobile_verified()
    def bag(self, request):
        try:
            order = Order.objects.get(user=request.user, status__in=('draft', 'pickup'))
            serializer = self.serializer_class(order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": "error message order does not exists"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist as e:
            return Response({"id": 400, "message": "order Does Not exisit!!!"}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def add(self, request):
        service_id = request.data.get('service_id')
        service = get_object_or_404(Service, pk=service_id)
        order = None

        try:
            order = Order.objects.get(user=request.user, status='draft')
            try:
                order_service = OrderService.objects.get(order=order, service=service)
                order_service.count += 1
                order_service.save()

            except OrderService.DoesNotExist:
                order_service = OrderService.objects.create(order=order, service=service)

        except Exception as e:
            order = Order.objects.create(user=request.user, status='draft')
            OrderService.objects.create(order=order, service=service)
            OrderStatus.objects.create(order=order, status='draft')

        finally:
            serializer = self.serializer_class(order)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    @mobile_verified()
    def bulk_service(self, request):
        services = request.data.get('services')

        if not isinstance(services,dict):
            raise Exception('services type invalid!!!')

        try:
            order = Order.objects.get(user=request.user, status='draft')
            OrderService.objects.filter(order=order).delete()
            try:
                with transaction.atomic():
                    for key in services:
                        service = Service.objects.filter(id=key).last()

                        if service is not None:
                            OrderService.objects.create(order=order, service=service, count=services[key])

            except Exception as e:
                return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"id": 200, "message": "services add to order"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
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
    @mobile_verified()
    def confirm(self, request):
        order = get_object_or_404(Order, user=request.user, defaults={'status': 'pickup'})
        order.status = 'confirmed'
        order.save()

        OrderStatus.objects.create(order=order, status='confirmed')

        return Response({"id": 200, "message": "order confirmed"}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    @mobile_verified()
    def address(self, request):
        try:
            lat = request.data.get('lat')
            long = request.data.get('long')
            address = request.data.get('address')
            state = request.data.get('status')
            period_time = request.data.get('period_time')
            date_pickup = request.data.get('date_pickup')

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

            try:
                order_address = OrderAddress.objects.get(order=order, status=status)
                order_address.address = address
                order_address.lat = lat
                order_address.long = long
                order_address.start_time = period_time_entity.start_time
                order_address.end_time = period_time_entity.end_time
                order_address.selected_date = main_datetime.datetime.strptime(date_pickup, "%Y-%m-%d").date()
                order_address.save()

            except:
                OrderAddress.objects.create(
                    order=order,
                    lat=lat,
                    long=long,
                    address=address,
                    start_time=period_time_entity.start_time,
                    end_time=period_time_entity.end_time,
                    selected_date=main_datetime.datetime.strptime(date_pickup, "%Y-%m-%d").date(),
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
    @mobile_verified()
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
            return Response({"id": 400, "message": "not found"}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def paid(self, request):
        try:
            order = Order.objects.get(user=request.user, status='pickup')
            order.status = 'paid'
            order.save()
            serializer = self.serializer_class(order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def confirm(self, request):
        try:
            order = Order.objects.get(user=request.user, status='paid')
            order.status = 'confirmed'
            order.save()

            serializer = self.serializer_class(order)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def order_list(self, request):
        orders = Order.objects.filter(status__in=(
            'confirmed', 'on_the_way_delivered',  'on_the_way_pickedup', 'delivered', 'pickedup'))
        serializer = OrderSerializer(orders, many=True)
        return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    @mobile_verified()
    def operate(self, request):
        try:
            state = request.data.get('state')
            order_id = request.data.get('order_id')

            if state is None and state not in ('on_the_way_delivered', 'delivered', 'pickedup', 'on_the_way_pickedup'):
                raise Exception('state not valid')

            if order_id is None:
                raise Exception('order id not in request')

            order = Order.objects.get(id=order_id, status__in=('confirmed',
                                                               'on_the_way_delivered',
                                                               'on_the_way_pickedup',
                                                               'delivered',
                                                               'pickedup'))
            order.status = state
            order.save()

            serializer = OrderSerializer(order)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": "order not found"}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def ongoing(self, request):
        try:
            orders = Order.objects.filter(user=request.user).exclude(status__in=('draft', 'pickup', 'paid', 'done'))
            serializer = OrderSerializer(orders, many=True)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def past(self, request):
        try:
            orders = Order.objects.filter(user=request.user, status='done')
            serializer = OrderSerializer(orders, many=True)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)


class PeriodViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = PeriodTime.objects.all()
    serializer_class = PeriodTimeSerializer


class OrderMessageViewSet(DefaultsMixin, AuthMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = OrderMessage.objects.all()
    serializer_class = OrderMessageSerializer

    @list_route(methods=['post'])
    @mobile_verified()
    def send(self, request):
        try:
            order_id = request.data.get('order_id')
            text_message = request.data.get('text_message')

            if order_id is None:
                raise Exception('order id not found')

            if text_message is None:
                raise Exception('text message not found')

            order = Order.objects.get(id=order_id)
            OrderMessage.objects.create(sender=request.user, order=order, text_message=text_message)

            return Response({"id": 200, "message": "message sent!!!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": e}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def inbox(self, request):
        try:
            order_id = request.data.get('order_id')

            if order_id is None:
                raise Exception('order id not found')

            order = Order.objects.get(id=order_id)
            messages = OrderMessage.objects.filter(order=order).order_by('created_date')

            serializer = self.serializer_class(messages, many=True)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @list_route(methods=['post'])
    @mobile_verified()
    def show(self, request):
        try:
            order_id = request.data.get('order_id')
            if order_id is None:
                raise Exception('order id not found')

            order = Order.objects.get(id=order_id)
            tickets = Ticket.objects.filter(order=order)

            serializer = self.serializer_class(tickets, many=True)
            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def change(self, request):
        try:
            ticket_id = request.data.get('ticket_id')
            state = request.data.get('state')

            if ticket_id is None:
                raise Exception('ticket_id not found')

            if state is None:
                raise Exception('state not found')

            ticket = Ticket.objects.get(id=ticket_id)

            if ticket.state == 'close':
                raise Exception('ticket close')

            ticket.state = state
            ticket.save()
            serializer = self.serializer_class(ticket)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def create_ticket(self, request):
        try:
            subject = request.data.get('subject')
            department = request.data.get('department')
            persiority = request.data.get('persiority')
            order_id = request.data.get('order_id')
            message = request.data.get('message')

            if subject is None:
                raise Exception('subject not found')

            if department is None:
                raise Exception('department not found')

            if persiority is None:
                raise Exception('persiority not found')

            if order_id is None:
                raise Exception('order_id not found')

            order = Order.objects.get(id=order_id)
            ticket = Ticket.objects.create(
                order=order,
                department=department,
                persiority=persiority,
                subject=subject
            )

            TicketMessage.objects.create(ticket=ticket, message=message)

            serializer = self.serializer_class(ticket)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    @mobile_verified()
    def send_message(self, request):
        try:
            ticket_id = request.data.get('ticket_id')
            message = request.data.get('message')
            state = request.data.get('state')

            if ticket_id is None:
                raise Exception('subject not found')

            if message is None:
                raise Exception('message not found')

            ticket = Ticket.objects.get(id=ticket_id)

            if ticket.state == 'close':
                raise Exception('ticket close')

            TicketMessage.objects.create(ticket=ticket, message=message)

            ticket.state = state
            ticket.save()

            serializer = self.serializer_class(ticket)

            return Response({"id": 200, "message": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"id": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
