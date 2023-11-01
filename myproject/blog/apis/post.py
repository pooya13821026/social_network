from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from myproject.api.mixins import ApiAuthMixin
from myproject.api.pagination import LimitOffsetPagination, get_paginated_response_context
from myproject.blog.models import Post
from myproject.blog.selectors.posts import post_list, post_detail
from myproject.blog.services.posts import create_post


class PostApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=100, required=False)
        search = serializers.CharField(max_length=100, required=False)
        created_at__range = serializers.CharField(max_length=100, required=False)
        author__in = serializers.CharField(max_length=100, required=False)
        slug = serializers.CharField(max_length=100, required=False)
        content = serializers.CharField(max_length=100, required=False)

    class InputSerializer(serializers.Serializer):
        content = serializers.CharField(max_length=100)
        title = serializers.CharField(max_length=100)

    class OutputSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField('get_author')
        url = serializers.SerializerMethodField('get_url')

        class Meta:
            model = Post
            fields = ('url', 'title', 'author')

        def get_author(self, post):
            return post.author.email

        def get_url(self, post):
            request = self.context.get('request')
            path = reverse('api:blog:post_detail', args=(post.slug,))
            return request.build_absolute_uri(path)

    @extend_schema(responses=OutputSerializer, request=InputSerializer)
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_post(
                user=request.user,
                content=serializer.validated_data.get('content'),
                title=serializer.validated_data.get('title'),
            )
        except Exception as ex:
            return Response(
                {'detail': 'Databes Error - ' + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query, context={'request': request}).data)

    @extend_schema(parameters=[FilterSerializer], responses=OutputSerializer)
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        try:
            query = post_list(filters=filters_serializer.validated_data, user=request.user)
        except Exception as ex:
            return Response(
                {'detail': 'Filter Error - ' + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=query,
            request=request,
            view=self,
        )


class PostDetailApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class OutputDetailSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField('get_author')

        class Meta:
            model = Post
            fields = ('author', 'slug', 'title', 'content', 'created_at', 'updated_at')

        def get_author(self, post):
            return post.author.email

    @extend_schema(responses=OutputDetailSerializer)
    def get(self, request, slug):
        try:
            query = post_detail(slug=slug, user=request.user)
        except Exception as ex:
            return Response(
                {'detail': 'Filter Error -' + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.OutputDetailSerializer(query)
        return Response(serializer.data)
