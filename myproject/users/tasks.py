from celery import shared_task

from myproject.users.services import profile_count_update


@shared_task
def profile_update():
    profile_count_update()
