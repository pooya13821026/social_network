from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from django_filters import FilterSet, CharFilter
from rest_framework.exceptions import APIException

from myproject.blog.models import Post


class PostFilter(FilterSet):
    search = CharFilter(method='filter_search')
    authon__in = CharFilter(method='filter_authon__in')
    created_at__range = CharFilter(method='filter_created_at__range')

    def filter_authon__in(self, queryset, name, value):
        limit = 10
        authons = value.split(',')
        if len(authons) > limit:
            raise APIException(f'You cannot add more then {len(authons)} username')
        return queryset.filter(authon__username__in=authons)

    def filter_created_at__range(self, queryset, name, value):
        limit = 2
        created_at__in = value.split(',')
        if len(created_at__in) > limit:
            raise APIException('Plase just add two created_at with , in the middle')

        created_at_0, created_at_1, = created_at__in

        if not created_at_1:
            created_at_1 = timezone.now()

        if not created_at_0:
            return queryset.filter(created_at__date__lt=created_at_1)
        return queryset.filter(created_at__date__range=(created_at_0, created_at_1))

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector('title')).filter(search=value)

    class Meta:
        model = Post
        fields = ('slug', 'title')
