from django.shortcuts import render_to_response
from django.template.context import RequestContext
from core.models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

@login_required
def index(request):
    user_list = GenericProfile.objects.filter (user__email__iexact=request.user.email)
    return render_to_response('home_index.html',
                { 'user': user_list[0] }, 
                context_instance=RequestContext(request))

@login_required
def send_invite (request):
    if 'recipient_id' in request.GET:
        user = request.user
        user_list = GenericProfile.objects.filter (user__id=request.GET['recipient_id'])
        if user_list:
            invite = Invite()
            invite.recipient = user_list[0]
            invite.status = 'pending'
            invite.message = 'mensagem de convite'
    return (Http404())

@login_required
def accept_invite (request):
    if 'invite_id' in request.GET:
        invite_list = Invite.objects.filter (id=request.GET['invite_id'])
        if invite_list and invite_list[0].status == 'pending':
            sender_list = GenericProfile.objects.filter (invite__id=invite_list[0].id)
            recipient = invite_list[0].recipient
            if sender_list:
                invite_list[0].status = 'accepted'
                sender_list[0].friends.add (recipient)
                recipient.friends.add (sender_list[0])
    return (Http404())





