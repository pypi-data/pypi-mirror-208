from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

# This was used to test something... But i do not remember what it was for...
@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    print("User logged in")

@receiver(user_logged_out)
def post_login(sender, user, request, **kwargs):
    print("User logged out")
