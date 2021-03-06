from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from base.models import Base
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


@python_2_unicode_compatible
class Category(Base):
    name = models.CharField(_('name'), max_length=50)
    icon = models.ImageField(_('icon'), upload_to='category_icon')
    details = models.TextField(_('details'), null=True, blank=True)
    discount = models.PositiveIntegerField(_('discount'), default=0)
    notification = models.CharField(_('notification'), max_length=250, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='parent', related_name='sub_categories', null=True, blank=True)

    class Meta:
        db_table = 'categories'
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class Service(Base):
    name = models.CharField(_('name'), max_length=50)
    icon = models.ImageField(_('icon'), upload_to='service_icon')
    notification = models.CharField(_('notification'), max_length=250, null=True, blank=True)
    details = models.TextField(_('details'), null=True, blank=True)
    price = models.PositiveIntegerField(_('price'), default=0)
    discount = models.PositiveIntegerField(_('discount'), default=0)
    duration = models.PositiveIntegerField(_('duration'), blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_('category'), related_name='services')

    class Meta:
        db_table = 'services'
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        return '{}'.format(self.name)


@python_2_unicode_compatible
class PeriodTime(Base):
    start_time = models.PositiveIntegerField(_('start time'), validators=[MaxValueValidator(24), MinValueValidator(1)])
    end_time = models.PositiveIntegerField(_('end time'), validators=[MaxValueValidator(24), MinValueValidator(1)])

    class Meta:
        db_table = 'period_times'
        verbose_name = _('period_time')
        verbose_name_plural = _('period_times')

    def __str__(self):
        return '{}-{}'.format(self.start_time, self.end_time)