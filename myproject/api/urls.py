from django.urls import path, include

urlpatterns = [
    # path('blog/', include(('myproject.blog.urls', 'blog')))
    path('uses/', include(('myproject.users.urls', 'users')))
]
