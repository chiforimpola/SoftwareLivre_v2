from django.shortcuts import render_to_response
from django.template.context import RequestContext
from core.models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
import os


@login_required
def init(request):
    generic_profile_list = GenericProfile.objects.filter(logged=True)
    logged_profile = GenericProfile.objects.filter (user__id=request.user.id)[0]
    result = []
    for generic_profile in generic_profile_list:
        if generic_profile.user.id != request.user.id:
            result.append(generic_profile)

    if result:
        return render_to_response('chat_init.html',
                    { 'profile_list': result,
                      'logged_profile': logged_profile
                    },
                    context_instance=RequestContext(request))
    else:
        return render_to_response('chat_init_no_users.html',
                    { 'profile_list': result },
                    context_instance=RequestContext(request))


@login_required
def message_post (request):
    if request.method == 'POST' and 'message_contents' in request.POST and request.POST['message_contents']:
        profile = GenericProfile.objects.filter (user__id=request.user.id)
        formated_message = ('%s diz %s <br/>') % (
            profile[0].full_name,
            request.POST['message_contents']
        )
        history_file = open('history', 'a+')
        history_file.write(formated_message)
        history_file.close()
        return (HttpResponse(formated_message))
    raise (Http404())


@login_required
def return_history (request):
    if os.path.isfile('history'):
        history_file = open('history')
        return (HttpResponse(history_file.read()))
    raise (Http404())


