from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from base.models import Base
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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
    name = models.CharField(_('name'), max_length=50, blank=True)
    profile_avatar = models.ImageField(_('profile avatar'), upload_to='static/profile', null=True, blank=True)
    sur_name = models.CharField(_('Surname'), max_length=50, blank=True)
    mobile = models.CharField(_('mobile'), max_length=200, unique=True, default='')
    mobile_verified = models.BooleanField(_('mobile_verified'), default=False)
    address = models.TextField(_('address'), default='')
    user = models.OneToOneField(User, verbose_name=_('user'), related_name='user')

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        db_table = 'profiles'

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class VerificationMobile(Base):
    verification_code = models.CharField(_('verification code'), max_length=5, blank=True)
    expired = models.BooleanField(_('expired'), default=False)
    profile = models.ForeignKey(Profile, verbose_name=_('profile'), related_name='verification_codes')

    def __str__(self):
        return '{}'.format(self.verification_code)

