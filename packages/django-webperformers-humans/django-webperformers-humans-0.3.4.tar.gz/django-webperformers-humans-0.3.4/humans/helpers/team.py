from django.http import HttpRequest
from django.db.models import QuerySet
from humans.models import Human

def getTeam(request:HttpRequest) -> QuerySet:
    team:QuerySet
    if request.user.is_superuser:
        team:QuerySet = Human.objects.all().order_by("position")
    else:
        team:QuerySet = Human.objects.filter(isPublished=True).order_by("position")
    return team