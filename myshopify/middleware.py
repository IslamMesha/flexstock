import shopify
from django.conf import settings


class ConfigurationError(Exception):
    pass


class LoginProtection:
    def __init__(self, get_response):
        self.get_response = get_response
        if not settings.SHOPIFY_API_KEY or not settings.SHOPIFY_API_SECRET:
            raise ConfigurationError("SHOPIFY_API_KEY and SHOPIFY_API_SECRET must be set in settings")
        shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        if hasattr(request, 'session') and 'shopify' in request.session:
            shopify_session = shopify.Session(request.session['shopify']['shop_url'], settings.API_VERSION)
            shopify_session.token = request.session['shopify']['access_token']
            shopify.ShopifyResource.activate_session(shopify_session)

    @staticmethod
    def process_response(request, response):
        shopify.ShopifyResource.clear_session()
        return response
