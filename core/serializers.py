from django.db.models import Case, When, F, Q, Sum
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from .models import Museum, Quiz, Question, UpcomingEvent, UserAnswer


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class QuizItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    user_answer = serializers.SerializerMethodField()
    user_answer_correct = serializers.SerializerMethodField()
    is_answered = serializers.SerializerMethodField()

    def get_image_url(self, instance):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(instance.image.url)
        return instance.image.url

    def get_user_answer_correct(self, instance):
        answers = self.context.get('answers', {})
        if answers.get(instance.pk):
            return answers[instance.pk].get('correct') is True

    def get_user_answer(self, instance):
        answers = self.context.get('answers', {})
        if answers.get(instance.pk):
            return answers[instance.pk].get('answer')

    def get_is_answered(self, instance):
        return self.get_user_answer(instance) is not None

    class Meta:
        model = Question
        fields = ('id',
                  'question',
                  'answer',
                  'options',
                  'hint',
                  'trivia',
                  'image_url',
                  'is_answered',
                  'user_answer',
                  'user_answer_correct', )


class QuizSerializer(DynamicFieldsModelSerializer):
    questions = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    points = serializers.SerializerMethodField()
    museum_name = serializers.SlugRelatedField(
        source='museum',
        slug_field='name',
        read_only=True, )

    def get_points(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            qs = UserAnswer.objects.filter(
                user=request.user,
                question__quiz=instance,
                correct=True, ).aggregate(Sum('question__points'))
            return qs['question__points__sum'] or 0

    def get_questions(self, instance):
        request = self.context.get('request')
        queryset = instance.question_set.all()
        if request and request.user.is_authenticated:
            answers = UserAnswer.objects.filter(
                user=request.user,
                question__quiz=instance).values('answer', 'correct', 'question_id')
            answers = {a['question_id']: a for a in answers}
        else:
            answers = {}

        context = {'answers': answers, 'request': self.context.get('request')}
        serialized = QuizItemSerializer(
            instance=queryset.distinct('pk'),
            many=True,
            context=context, )
        return serialized.data

    class Meta:
        model = Quiz
        fields = ('id', 'name', 'category', 'questions', 'points', 'museum_name')


class UpcomingEventSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(instance.image.url)
        return instance.image.url

    class Meta:
        model = UpcomingEvent
        fields = ('name', 'date', 'image')


class MuseumSerializer(gis_serializers.GeoModelSerializer):
    # distance = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    upcoming_events = serializers.SerializerMethodField()
    quizzes = QuizSerializer(
        many=True,
        read_only=True,
        fields=('id',
                'name',
                'museum_name',
                'category', ),
        source='quiz_set', )

    def get_distance(self, obj):
        params = self.context.get('request').query_params
        lat, lng = params.get('lat'), params.get('lng')
        if lat and lng:
            query_point = GEOSGeometry('POINT({} {})'.format(lng, lat), srid=4326)
            return obj.coordinates.distance(query_point) * 100

    def get_images(self, instance):
        images = instance.images.all()
        request = self.context.get('request')
        if request:
            image_urls = [request.build_absolute_uri(x.image.url) for x in images]
            return image_urls
        return list(map(lambda x: x.image.url, images))

    def get_thumbnail(self, instance):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(instance.thumbnail.url)
        return instance.thumbnail.url

    def get_upcoming_events(self, instance):
        upcoming_events = instance.upcoming_events.filter(status=UpcomingEvent.ACTIVE)
        serializer = UpcomingEventSerializer(
            instance=upcoming_events,
            many=True,
            context={
                'request': self.context.get('request')
            }, )
        return serializer.data

    def to_representation(self, obj):
        ret = super(MuseumSerializer, self).to_representation(obj)
        coordinates = ret.pop('coordinates')
        ret['coordinates'] = coordinates['coordinates']
        return ret

    class Meta:
        model = Museum
        fields = ('id',
                  'address',
                  'city',
                  'coordinates',
                  'country',
                  'description',
                  'distance',
                  'thumbnail',
                  'images',
                  'name',
                  'upcoming_events',
                  'quizzes',
                  'rating', )


class UserAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects)
    answer = serializers.CharField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        question = validated_data.pop('question')
        user = validated_data.pop('user')

        validated_data['correct'] = question.answer == validated_data['answer']
        instance, _ = self.Meta.model.objects.update_or_create(
            question=question,
            user=user,
            defaults=validated_data, )
        return instance

    def update(self, instance, validated_data):
        raise NotImplementedError()

    class Meta:
        model = UserAnswer
        fields = ('question', 'answer', 'correct', 'user')
        read_only_fields = ('correct', )
        validators = []
