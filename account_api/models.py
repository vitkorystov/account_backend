from django.db import models
import uuid


class AccountsModel(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, verbose_name='Uuid')
    name = models.TextField(null=False, default='', verbose_name='ФИО')
    balance = models.IntegerField(null=False, default=0, verbose_name='Баланс')
    hold = models.IntegerField(null=False, default=0, verbose_name='Холд')
    status = models.BooleanField(null=False, verbose_name='Статус')

    class Meta:
        verbose_name_plural = 'Абоненты'
        verbose_name = 'Абонент'
        ordering = ['-name']
