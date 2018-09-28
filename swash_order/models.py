from django.db import models
from base.models import Base
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from swash_service.models import Service
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Order(Base):
    STATUS_TYPE = (
        ('draft', 'draft'),
        ('confirmed', 'confirmed'),
        ('confirmed', 'confirmed'),
        ('paid', 'paid'),
        ('pickup', 'pickup'),
        ('progress', 'progress'),
        ('packing', 'packing'),
        ('on_the_way', 'on_the_way'),
        ('delivered', 'delivered'),
        ('pending', 'pending'),
        ('cancel', 'cancel'),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUS_TYPE, default='draft')
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='orders')

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        db_table = 'orders'

    def __str__(self):
        return '{}'.format(self.id)

    @property
    def price(self):
        return 0
    
    @property
    def discount(self):
        return 0
    
    @property
    def pure(self):
        return self.price - self.discount


@python_2_unicode_compatible
class OrderStatus(Base):
    STATUS_TYPE = (
        ('draft', 'draft'),
        ('confirmed', 'confirmed'),
        ('confirmed', 'confirmed'),
        ('paid', 'paid'),
        ('pickup', 'pickup'),
        ('progress', 'progress'),
        ('packing', 'packing'),
        ('on_the_way', 'on_the_way'),
        ('delivered', 'delivered'),
        ('pending', 'pending'),
        ('cancel', 'cancel'),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUS_TYPE, default='draft')
    order = models.ForeignKey(Order, verbose_name=_('order'), related_name='states')

    class Meta:
        verbose_name = _('order_status')
        verbose_name_plural = _('order_states')
        db_table = 'order_states'

    def __str__(self):
        return '{}'.format(self.status)


@python_2_unicode_compatible
class OrderService(Base):
    service = models.ForeignKey(Service, verbose_name=_('services'), related_name='services')
    order = models.ForeignKey(Order, verbose_name=_('order'), related_name='orders')
    count = models.PositiveIntegerField(_('count'), default=1)

    class Meta:
        verbose_name = _('order_service')
        verbose_name_plural = _('order_services')
        db_table = 'order_services'
        unique_together = ('order', 'service')

    def __str__(self):
        return '{}'.format(self.id)


@python_2_unicode_compatible
class OrderAddress(Base):
    STATE = (
        ('pickup', 'pickup'),
        ('delivery', 'delivery')
    )
    lat = models.DecimalField(_('lat'), max_digits=20, decimal_places=20)
    long = models.DecimalField(_('long'), max_digits=20, decimal_places=20)
    address = models.TextField(_('address'), null=True, blank=True)
    status = models.CharField(_('status'), max_length=10, choices=STATE, default='pickup')
    order = models.ForeignKey(Order, verbose_name=_('order'), related_name='addresses')

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        db_table = 'addresses'
        unique_together = ('order', 'status')

    def __str__(self):
        return '{}'.format(self.id)