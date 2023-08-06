from core_models import constants as consts
from django.conf import settings


def constants_and_settings(request):
    return {**vars(consts), **vars(settings)}

