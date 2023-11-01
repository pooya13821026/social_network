from django.db.models import QuerySet

from myproject.blog.filters import PostFilter
from myproject.blog.models import Subscription, Post
from myproject.users.models import BaseUser


def get_subscribers(*, user: BaseUser) -> QuerySet[Subscription]:
    return Subscription.objects.filter(subscriber=user)


def post_detail(*, slug: str, user: BaseUser, self_include: bool = True) -> Post:
    subscribtions = list(Subscription.objects.filter(subscriber=user).values_list("target", flat=True))
    if self_include:
        subscribtions.append(user.id)

    return Post.objects.get(slug=slug, author__in=subscribtions)


# def post_list(*, filters=None, user: BaseUser, self_include: bool = True) -> QuerySet[Post]:
#     filters = filters or {}
#     subscribtions = list(Subscription.objects.filter(subscriber=user).values_list('target', flat=True)
#     if self_include:
#         subscribtions.append(user.id)
#     if subscribtions:
#         qs = Post.objects.filter(author__in=subscribtions)
#         return PostFilter(filters, qs).qs
#     return Post.objects.none()


def post_list(*, filters=None, user: BaseUser, self_include: bool = True) -> QuerySet[Post]:
    filters = filters or {}
    subscribtions = list(Subscription.objects.filter(subscriber=user).values_list("target", flat=True))
    if self_include:
        subscribtions.append(user.id)
    if subscribtions:
        qs = Post.objects.filter(author__in=subscribtions)
        return PostFilter(filters, qs).qs
    return Post.objects.none()