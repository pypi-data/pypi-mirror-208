from django.urls import path, include
from humans.views import teamPageView, personView, humans_txt

urlpatterns = [
    path('team/', teamPageView, name="humansTeamView"),
    path('team/<slug:personSlug>/', personView, name="humansPersonPageView"),
    path("humans.txt", humans_txt),
]