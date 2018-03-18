from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.facebook.views import login_by_token
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (response,
                            decorators,
                            viewsets,
                            exceptions,
                            permissions,
                            reverse, )
from .models import Museum, Quiz, UserAnswer
from .serializers import (QuizSerializer,
                          MuseumSerializer,
                          UserAnswerSerializer, )


class QuizAPI(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects

    @transaction.atomic
    @decorators.detail_route(
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated, ), )
    def submit(self, request, pk):
        serialized = UserAnswerSerializer(
            data=request.data.get('answers', []),
            context=self.get_serializer_context(),
            many=True, )
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return redirect(reverse.reverse_lazy("core:quiz-detail", kwargs={'pk': int(pk)}))

    def update(self, request, *args, **kwargs):
        raise NotImplementedError()

    def destroy(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied()


class MuseumAPI(viewsets.ModelViewSet):
    serializer_class = MuseumSerializer
    queryset = Museum.objects

    def update(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied()

    def destroy(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied()

    def get_queryset(self):
        params = self.request.query_params
        lat, lng = params.get('lat'), params.get('lng')
        queryset = self.queryset
        if lat and lng:
            radius = params.get('radius', 10000)  # default radius to 5km
            pnt = GEOSGeometry('POINT({} {})'.format(lng, lat), srid=4326)
            queryset = self.queryset.filter(coordinates__distance_lte=(pnt, radius))
        return queryset


def login_debug(request):
    return render(request, "login.html")


def get_ranked():
    return UserAnswer.objects.filter(correct=True).values('user_id').annotate(
        points=Sum('question__points'),
        first_name=F('user__first_name'),
        last_name=F('user__last_name'),
        username=F('user__username'), ).order_by('-points')


def get_user_profiles(user_ids):
    social = SocialAccount.objects.filter(user_id__in=user_ids).distinct('user_id')
    return {s.user_id: s for s in social}


def get_facebook_profile_image_url(social):
    """
    Args:
        social (SocialAccount):
    """
    if not social:
        return

    return 'https://graph.facebook.com/{}/picture?type=normal'.format(social.uid)


@decorators.api_view(http_method_names=['get'])
def leaderboard(request):
    ranked = get_ranked()
    profiles = get_user_profiles(ranked.values_list('user_id', flat=True))

    resp = [{
        "image_url": get_facebook_profile_image_url(profiles.get(r['user_id'])),
        "name": (' '.join([r['first_name'], r['last_name']]).strip() or r['username']),
        "points": r['points'],
    } for r in ranked]
    return response.Response(resp)


@decorators.api_view(http_method_names=['get'])
@decorators.permission_classes((permissions.IsAuthenticated, ))
def profile(request):
    social_profile = request.user.socialaccount_set.first()
    if not social_profile:
        user = {}
    else:
        user = social_profile.extra_data

    quizzes = UserAnswer.objects.filter(user=request.user)
    points = quizzes.filter(correct=True).aggregate(Sum('question__points'))
    attempted_count = quizzes.count()
    if attempted_count > 0:
        accuracy = (quizzes.filter(correct=True).count() / attempted_count) * 100
    else:
        accuracy = 0.0

    ranked = get_ranked().values_list('user_id', flat=True)
    try:
        rank = list(ranked).index(request.user.pk) + 1
    except ValueError:
        rank = None

    extra = {
        'accuracy': '{:.1f}'.format(accuracy),
        'points': points['question__points__sum'] or 0,
        'quiz_count': quizzes.distinct('question__quiz').count(),
        'rank': rank,
    }
    user.update(extra)
    return response.Response(user)


@csrf_exempt
def login(request):
    return csrf_exempt(login_by_token)(request)


@cache_page(86400)
def privacy(request):
    return render(request, "privacy.html")
