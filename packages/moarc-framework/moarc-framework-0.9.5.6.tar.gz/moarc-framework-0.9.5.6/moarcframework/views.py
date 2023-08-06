# Create your views here.

from django.http import JsonResponse

from .models import Menu, Config, MenuSerializer


def get_moarc_env(request):
    menus = Menu.objects.filter(active=True).all()
    configs = Config.prepared_configs()
    menus_serialized = MenuSerializer(data=menus, many=True)
    menus_serialized.is_valid()
    return JsonResponse({'menus': menus_serialized.data,
                         'configs': configs})
