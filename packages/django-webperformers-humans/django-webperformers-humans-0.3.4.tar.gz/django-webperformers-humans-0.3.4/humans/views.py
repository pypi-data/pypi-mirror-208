from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.conf import settings
from humans.models import Human
from humans.helpers.team import getTeam
from humans.helpers.generic import getBaseTemplate
from django.db.models import QuerySet
from django.views.decorators.http import require_GET
from django.utils.html import strip_tags

def teamPageView(request:HttpRequest):
    context:dict = {}
    getBaseTemplate(context)
    team:QuerySet = getTeam(request)
    if (team.__len__() > 0 or request.user.is_superuser):
        context["team"] = team
        return render(request, 'humans/teamPage.html', context=context)
    else:
        return HttpResponseNotFound()

def personView (request:HttpRequest, personSlug:str):
    context:dict = {}
    getBaseTemplate(context)
    try:
        person:Human = Human.objects.get(customSlug=personSlug)
        context["person"] = person
        return render(request, 'humans/personPage.html', context=context)
    except Human.DoesNotExist:
        return HttpResponseNotFound()

@require_GET
def humans_txt(request):
    response:str = "/* TEAM */\n\n"
    team:QuerySet = getTeam(request)
    if (team.__len__() > 0 or request.user.is_superuser):
        person:Human
        for person in team:
            personString:str = "--------------------------------------------\n"
            personString = personString + f"""Title: {person.position}\nName: {person.name}\nSite: {person.websiteUrl}\nTwitter: {person.twitterUrl}\nLinkedIn: {person.linkedInUrl}\nAbout:\n{strip_tags(person.shortDescription)}\n"""
            personString = personString + "--------------------------------------------\n"
            response = response + personString
        return HttpResponse (response, content_type="text/plain")
    else:
        return HttpResponseNotFound()