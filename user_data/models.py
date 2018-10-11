# import datetime
from datetime import datetime
import pytz
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from base.models import Base
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from swash_order.models import Order


@python_2_unicode_compatible
class Device(Base):
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='devices', null=True)
    device_model = models.CharField(_('device model'), max_length=100)
    device_id = models.CharField(_('device model'), max_length=500)

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')
        db_table = 'devices'

    def __str__(self):
        return '{}-{}'.format(self.device_id, self.device_id)


@python_2_unicode_compatible
class Account(Base):
    ACCOUNT_TYPE = (
        ('google', 'google'),
        ('facebook', 'facebook'),
        ('apple', 'apple'),
    )
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='accounts', null=True)
    account_type = models.CharField(_('account type'), max_length=10, choices=ACCOUNT_TYPE, default='google')
    account_id = models.CharField(_('account id'), max_length=200)

    class Meta:
        unique_together = ('account_type', 'account_id')
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        db_table = 'accounts'

    def __str__(self):
        return '{}-{}'.format(self.account_type, self.account_id)


@python_2_unicode_compatible
class Profile(Base):
    SEX_TYPE = (
        ('male', 'male'),
        ('female', 'female')
    )

    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    profile_pic_url = models.ImageField(_('profile avatar'), upload_to='profile', null=True, blank=True)
    mobile_number = models.CharField(_('mobile number'), max_length=20, null=True, blank=True)
    mobile_verified = models.BooleanField(_('mobile verified'), default=False)
    phone_number = models.CharField(_('phone number'), max_length=20, null=True, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, verbose_name=_('user'), related_name='profile')

    age = models.PositiveIntegerField(_('age'), default=20)
    sex = models.CharField(_('sex'), max_length=6, choices=SEX_TYPE, default='male')

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        db_table = 'profiles'

    def __str__(self):
        return '{}-{}'.format(self.first_name, self.last_name)

    @classmethod
    def is_active(cls, user):
        try:
            profile = cls.objects.get(user=user)
            return profile.mobile_verified
        except Exception as e:
            return False


@python_2_unicode_compatible
class VerificationMobile(Base):
    verification_code = models.CharField(_('verification code'), max_length=5, blank=True)
    expired = models.BooleanField(_('expired'), default=False)
    profile = models.ForeignKey(Profile, verbose_name=_('profile'), related_name='verification_codes')

    def __str__(self):
        return '{}'.format(self.verification_code)


@python_2_unicode_compatible
class Verification(Base):
    verification_code = models.CharField(_('verification code'), max_length=8, blank=True)
    profile = models.ForeignKey(Profile, verbose_name=_('profile'), related_name='devices')

    class Meta:
        db_table = 'verification'
        verbose_name = _('verification')
        verbose_name_plural = _('verification')

    def __str__(self):
        return '{}-{}'.format(self.profile.mobile_number, self.verification_code)

    @classmethod
    def is_verified(cls, mobile_no, verification_code, user):
        try:
            verification = cls.objects.get(
                profile=user.profile
            )

            delta = datetime.now(tz=pytz.utc) - verification.created_date
            minute, seconds = divmod(delta.days * 86400 + delta.seconds, 60)
            if minute <= 1 and seconds < 60:
                return True, 'verification code accepted', verification.profile.user.username

            return False, 'verification code not accepted', None

        except:
            return False, 'profile or verification code not found', None


@python_2_unicode_compatible
class Ticket(Base):
    DEPARTMENT_TYPE = (
        ('payment', 'payment'),
        ('technical', 'technical'),
    )

    PERSIORITY_TYPE = (
        ('normal', 'normal'),
        ('hight', 'hight'),
        ('urgent', 'urgent'),
    )

    STATES = (
        ('open', 'open'),
        ('unread_department', 'unread_department'),
        ('unread_user', 'unread_user'),
        ('close', 'close'),
    )

    subject = models.CharField(_('subject'), max_length=50)
    department = models.CharField(_('department'), max_length=40, choices=DEPARTMENT_TYPE, default='payment')
    persiority = models.CharField(_('persiority'), max_length=40, choices=PERSIORITY_TYPE, default='normal')
    order = models.ForeignKey(Order, verbose_name=_('order'), related_name='tickets')
    state = models.CharField(_('state'), max_length=40, choices=STATES, default='open')

    class Meta:
        db_table = 'ticket'
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')

    def __str__(self):
        return '{}-{}'.format(self.subject, self.order.id)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        TicketHistory.objects.create(status=self.state, ticket=self)

        super(Ticket, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


@python_2_unicode_compatible
class TicketMessage(Base):
    ticket = models.ForeignKey(Ticket, verbose_name=_('ticket'), related_name='messages')
    message = models.CharField(_('message'), max_length=200)

    class Meta:
        db_table = 'ticket_message'
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')

    def __str__(self):
        return '{}-{}'.format(self.subject, self.order.id)


@python_2_unicode_compatible
class TicketHistory(Base):
    status = models.CharField(_('status'), max_length=30)
    ticket = models.ForeignKey(Ticket, verbose_name=_('ticket'), related_name='states')

    class Meta:
        db_table = 'ticket_history'
        verbose_name = _('ticket_history')
        verbose_name_plural = _('ticket_histories')

    def __str__(self):
        return '{}'.format(self.status)


def create_user_dependency(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, gem=100)


signals.post_save.connect(create_user_dependency, sender=User)