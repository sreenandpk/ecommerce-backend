from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Postgres is case-sensitive, so we must normalize or use iexact
        email = username or kwargs.get("email") or kwargs.get("username")
        
        if email is None or password is None:
            return None
            
        try:
            # Check for user with case-insensitive email
            user = User.objects.get(email__iexact=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        return None