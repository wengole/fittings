from . import urls
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook


class FittingMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Fittings and Doctrines',
                              'fa fa-icon-list-alt fa-fw', 'fittings:test',
                              navactive=['fittings:'])

        def render(self, request):
            if request.user.has_perm('fittings.access_fittings'):
                return MenuItemHook.render(self, request)
            return ''


@hooks.register('menu_item_hook')
def register_menu():
    return FittingMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'fittings', 'r^fittings/')
