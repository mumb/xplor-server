from django.conf.urls import url
from django.conf import settings
from django.urls import include, path
from rest_framework import routers
from core import views


class OptionalTrailingSlashRouter(routers.SimpleRouter):
    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalTrailingSlashRouter()
router.register('museums', views.MuseumAPI, base_name='museum')
router.register('quiz', views.QuizAPI, base_name='quiz')

app_name = 'core'

urlpatterns = (
    path('profile/', views.profile),
    path('leaderboard/', views.leaderboard),
    path('login', views.login),
    path('privacy/', views.privacy),
    path('', include(router.urls)),
)

if settings.DEBUG is True:
    urlpatterns += (url(r'.debug/login', views.login_debug),)
