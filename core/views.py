# -*- coding: utf-8 -*-

from django.contrib.auth import logout, authenticate, login
from django.core.urlresolvers import reverse
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from core.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from core.models import GenericProfile
from django.db import transaction
import json

# Views de Login e Logout.
from messenger.forms import LoginForm, CreateAccountForm

@transaction.commit_on_success
def create_account_view (request):
    user = request.user
    if user.is_authenticated():
        return (HttpResponseRedirect('/Home'))

    if request.method == 'POST':
        create_account_form = CreateAccountForm (request.POST)
        if not create_account_form.is_valid():
            return render_to_response('create_account.html', {'create_account_form': create_account_form},
              context_instance=RequestContext(request))
        create_account_form_data = create_account_form.cleaned_data
        user = User()
        user.username = create_account_form_data['email']
        user.email = create_account_form_data['email']
        user.set_password (create_account_form_data['password'])
        user.save()

        generic_profile = GenericProfile()
        generic_profile.user = user
        generic_profile.full_name = create_account_form_data['full_name']
        generic_profile.logged = True
        generic_profile.save()

        # Auto Login
        user = authenticate(username=user.username,
            password=create_account_form_data['password'])
        login(request, user)

        return HttpResponseRedirect ('/Home')
    else:
        create_account_form = CreateAccountForm()
        return render_to_response('create_account.html', {'create_account_form': create_account_form},
              context_instance=RequestContext(request))

def login_view(request):
    user = request.user
    if user.is_authenticated():
        # Usuario ja autenticado.
        profile = user.get_profile()
        return HttpResponseRedirect('/Home')

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if not login_form.is_valid():
            return render_to_response('login.html', {'login_form': login_form},
                context_instance=RequestContext(request))
        login_form_data = login_form.cleaned_data
        user = authenticate(username=login_form_data['email'], password=login_form_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # Login efetuado.
                profile = user.get_profile()
                profile.logged = True
                profile.save()
                if login_form_data['next_url']:
                    return HttpResponseRedirect(login_form_data['next_url'])
                return HttpResponseRedirect('/Home')
            else:
                # Conta desabilitada.
                return direct_to_template(request, 'i_inactive_account.html')
        else:
            # Login invalido.
            login_form._errors[NON_FIELD_ERRORS] = login_form.error_class([u'Login inválido.'])
            return render_to_response('login.html', {'login_form': login_form},
                context_instance=RequestContext(request))
    else:
        login_form = LoginForm()
        if 'next' in request.GET:
            login_form.fields['next_url'].initial = request.GET['next']
        return render_to_response('login.html', {'login_form': login_form},
            context_instance=RequestContext(request))


@login_required
def logout_view(request):
    profile = GenericProfile.objects.filter (user__id=request.user.id)
    profile = profile[0]
    profile.logged = False
    profile.save()
    logout(request)
    return redirect(reverse('core.views.login_view'))


def open_position_public_view(request, company_id, open_position_id):
    open_positions = OpenPosition.objects.filter(id=open_position_id)
    if open_positions:
        open_position_applied = False
        if request.user.id != None:
            if is_company_user_profile(request):
                parameters = ('%s%s') % ('?id=', open_position_id)
                reverse_url = reverse('platforms.companies.views.view_opened_position_view')
                full_url = ('%s%s') % (reverse_url, parameters)
                return HttpResponseRedirect(full_url)
            profile = IndividualUserProfile.objects.filter(user=request.user)[0]
            open_position_applied = profile in open_positions[0].candidates.all()

        open_position_location = '%s, %s, %s' % (
            open_positions[0].location.name,
            open_positions[0].location.get_region().name,
            open_positions[0].location.country.name_pt_br)

        return (render_to_response(
            'p_view_open_position.html',
                {
                'open_position': open_positions[0],
                'open_position_applied': open_position_applied,
                'open_position_location': open_position_location
            },
            context_instance=RequestContext(request)
        ))
    raise Http404()

def is_company_user_profile(request):
    if request.user.id != None:
        if CompanyUserProfile.objects.filter(user=request.user):
            return True
    return False


@login_required
def autocomplete_skills_expertise_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        skills = SkillOrExpertise.objects.filter(name__istartswith=q).all()[:10]
        list = []
        if skills:
            for skill in skills:
                dict = {}
                dict['name'] = skill.name
                dict['id'] = skill.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


def autocomplete_location_city_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        cities = City.objects.filter(Q(name__istartswith=q) | Q(name_no_accent__istartswith=q))[:50]
        list = []
        if cities:
            for city in cities:
                country = city.country
                region = city.get_region()
                dict = {}
                dict['name'] = "%s, %s, %s" % (city.name, region.name, country.name_pt_br)
                dict['id'] = city.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


def autocomplete_city_country_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        regions = Region.objects.filter(name__istartswith=q)[:50]
        list = []
        if regions:
            for region in regions:
                country = region.country
                dict = {}
                dict['name'] = "%s, %s" % (region.name, country.name_pt_br)
                dict['id'] = region.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_school_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        schools = School.objects.filter(name__istartswith=q).all()[:10]
        list = []
        if schools:
            for school in schools:
                dict = {}
                dict['name'] = school.name
                dict['id'] = school.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_company_or_organizarion_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        companies = CompanyOrOrganization.objects.filter(name__istartswith=q).all()[:10]
        list = []
        if companies:
            for company in companies:
                dict = {}
                dict['name'] = company.name
                dict['id'] = company.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_role_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        roles = Role.objects.filter(name__istartswith=q).all()[:10]
        list = []
        if roles:
            for role in roles:
                dict = {}
                dict['name'] = role.name
                dict['id'] = role.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_customer_company_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        customer_companies = CustomerCompany.objects.filter(trading_name__istartswith=q).all()[:10]
        list = []
        if customer_companies:
            for customer_company in customer_companies:
                dict = {}
                dict['name'] = customer_company.trading_name
                dict['id'] = customer_company.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_language_proficiency_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        languages = Language.objects.filter(
            Q(name_pt_br__istartswith=q) | Q(name_pt_br_no_accent__istartswith=q)
        ).all()[:10]
        list = []
        if languages:
            for language in languages:
                dict = {}
                dict['name'] = language.name_pt_br
                dict['id'] = language.id
                list.append(dict)
                for proficiency_level in LANGUAGE_PROFICIENCY_LEVEL_CHOICES:
                    dict = {}
                    dict['name'] = language.name_pt_br + '/' + proficiency_level[1]
                    dict['id'] = language.id
                    list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()


@login_required
def autocomplete_degree_json(request):
    if request.is_ajax():
        q = request.GET['q'].lstrip()
        degrees = Degree.objects.filter(name__istartswith=q).all()[:10]
        list = []
        if degrees:
            for degree in degrees:
                dict = {}
                dict['name'] = degree.name
                dict['id'] = degree.id
                list.append(dict)
        return HttpResponse(json.dumps(list), mimetype="application/json")
    raise Http404()
