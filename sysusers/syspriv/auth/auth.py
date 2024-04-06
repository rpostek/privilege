import win32api
import win32security
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import login


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
            if domain.lower() == 'bzmw':
                return username
            else:
                return None
        else:
            return None
    except:
        return None

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