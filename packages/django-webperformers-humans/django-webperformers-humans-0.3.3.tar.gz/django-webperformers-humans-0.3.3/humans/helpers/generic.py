from django.conf import settings

def getBaseTemplate(context:dict):
    context["baseTemplate"] = "base.html"
    if hasattr(settings, "HUMANS_BASE_TEMPLATE"):
        context["baseTemplate"] = settings.HUMANS_BASE_TEMPLATE