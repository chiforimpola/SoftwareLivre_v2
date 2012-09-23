# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import GenericProfile
from django.template.defaultfilters import slugify

class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User()
        user.email = raw_input('Email Address: ')
        while len(user.email.split('@')) == 1:
            print ('Wrong email address format!')
            user.email = raw_input('Email address: ')
        user.username = user.email
        user.set_password(user.email.split('@')[0])
        if GenericProfile.objects.filter(user__email__iexact=user.email):
            print('Email address already exists!')
            exit()
        user.save()

        generic_profile = GenericProfile()
        generic_profile.user = user
        generic_profile.full_name = user.username
        generic_profile.save()
