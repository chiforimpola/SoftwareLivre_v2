# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

INVITE_STATUS_CHOICES = (
    ('pending', 'Aguardando retorno'),
    ('accepted', 'Aceito'),
    ('refused', 'Recusado'),
    )

class GenericProfile(models.Model):
    user = models.OneToOneField(User, null=False)
    full_name = models.CharField(u'Nome de usuário', max_length=200, null=False, blank=False)
    friends = models.ManyToManyField ('self')
    logged =  models.BooleanField(u'Logado?', default=False, null=False)

    class Meta():
        verbose_name = u'Usuarios de sistema'
        verbose_name_plural = u'Usuários de sistema'
        db_table = u'generic_profile'

    def save(self):
        super (GenericProfile, self).save()

    def get_email(self):
        return (self.user.email)

    def __unicode__(self):
        return (self.get_email())


class Invite (models.Model):
    message = models.CharField(u'Conteúdo', max_length=200, null=False, blank=False)
    entities = models.ManyToManyField (GenericProfile, verbose_name=u'Destinatário', null=False)
    status = models.IntegerField(u'Status do convite', choices=INVITE_STATUS_CHOICES, null=False)

