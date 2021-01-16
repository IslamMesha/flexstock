from django.shortcuts import redirect
from django.urls import reverse


def shop_login_required(func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'session') or 'shopify' not in request.session:
            return redirect(reverse('login'))
        return func(request, *args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
