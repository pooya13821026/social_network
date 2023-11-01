from django.db import models
from django.core.exceptions import ValidationError
from myproject.common.models import BaseModel
from myproject.users.models import BaseUser


class Post(BaseModel):
    slug = models.SlugField(max_length=150, allow_unicode=True)
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=200)
    author = models.ForeignKey(BaseUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.slug


class Subscription(models.Model):
    subscriber = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='subs')
    target = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name='target')

    class Meta:
        unique_together = ('subscriber', 'target')

    def clean(self):
        if self.subscriber == self.target:
            raise ValidationError({'subscriber': ('subscriber cannot be equal to target',)})

    def __str__(self):
        return f'{self.subscriber.email}-{self.target.email}'
