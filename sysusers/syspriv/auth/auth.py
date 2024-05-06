import win32api
import win32security
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import get_user
from .. import models
from django.core.exceptions import ObjectDoesNotExist

def get_logged_ad_user(request):
    try:
        if 'x-iis-windowsauthtoken' in request.headers.keys():
            handle_str = request.headers['x-iis-windowsauthtoken']
            handle = int(handle_str, 16) # need to convert from Hex / base 16
            win32security.ImpersonateLoggedOnUser(handle)
            sid = win32security.GetTokenInformation(handle, 1)[0]
            username, domain, account_type = win32security.LookupAccountSid(None, sid)
            #user = win32api.GetUserName()
            win32security.RevertToSelf() # undo impersonation
            win32api.CloseHandle(handle) # don't leak resources, need to close the handle!
            try:
                config_domain = models.Config.objects.get(key='domain').value.lower()
            except ObjectDoesNotExist:
                config_domain = None
            if domain.lower() == config_domain:
                return username
            else:
                return None
        else:
            return None
    except:
        return None

'''
class DomainBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        username = get_logged_ad_user(request)
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user
                user = User(username=username)
                #user.is_staff = True
                #user.is_superuser = True
                user.save()
            login(request, user)
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
'''

class WindowsAuthenticationMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = get_user(request)
        if not request.user.is_authenticated:
            ad_username = get_logged_ad_user(request)
            if ad_username:
                try:
                    request.user = User.objects.get(username=ad_username)
                except User.DoesNotExist:
                    # Create a new user
                    user = User(username=ad_username)
                    user.save()
                    login(request, user)
        response = self.get_response(request)
        return response
