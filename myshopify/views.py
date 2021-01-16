import os
import shopify
import binascii
from django.conf import settings
from celery.decorators import task
from celery.utils.log import get_task_logger
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect

from myshopify.models import ShopifyProduct, ShopifyOrder

logger = get_task_logger(__name__)


def _return_address(request):
    return request.session.get('return_to') or reverse('login')


def login(request):
    # Ask user for their ${shop}.shopify.com address

    # If the ${shop}.shopify.com address is already provided in the URL,
    # just skip to authenticate
    if request.GET.get('shop'):
        return authenticate(request)
    return render(request, 'login.html', {})


def authenticate(request):
    shop = request.POST.get('shop')
    if shop:
        scope = settings.SHOPIFY_API_SCOPE
        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        redirect_uri = request.build_absolute_uri(reverse('finalize'))
        permission_url = shopify.Session(shop.strip(), settings.API_VERSION).create_permission_url(scope, redirect_uri,
                                                                                                   state)
        return redirect(permission_url)

    return redirect(_return_address(request))


@task(name="sync_shopify_products")
def sync_shopify_products(shop_url, access_token):
    logger.info("Sync Shopify Orders")

    session = shopify.Session(shop_url, settings.API_VERSION, access_token)
    shopify.ShopifyResource.activate_session(session)

    shopify_products = shopify.Product.find()

    not_found_products = []
    for product in shopify_products:
        try:
            ShopifyProduct.objects.get(product_id=product.id)
        except ShopifyProduct.DoesNotExist:
            not_found_product = ShopifyProduct(
                title=product.title,
                vendor=product.vendor,
                product_id=product.id,
                status=product.status,
                product_type=product.product_type,
            )
            not_found_products.append(not_found_product)

    ShopifyProduct.objects.bulk_create(not_found_products)

    logger.info("Products synced successfully!")
    return {'msg': "Products synced successfully!"}


@task(name="sync_shopify_orders")
def sync_shopify_orders(shop_url, access_token):
    logger.info("Sync Shopify Orders")

    session = shopify.Session(shop_url, settings.API_VERSION, access_token)
    shopify.ShopifyResource.activate_session(session)

    shopify_orders = shopify.Order.find()

    not_found_orders = []
    for order in shopify_orders:
        try:
            ShopifyOrder.objects.get(order_number=order.order_number)
        except ShopifyOrder.DoesNotExist:
            not_found_order = ShopifyOrder(
                order_number=order.order_number,
                user_id=order.user_id,
                gateway=order.gateway,
                name=order.name,
                note=order.note
            )
            not_found_orders.append(not_found_order)

    ShopifyOrder.objects.bulk_create(not_found_orders)

    logger.info("Orders synced successfully!")
    return {'msg': "Orders synced successfully!"}


def finalize(request):
    shop_url = request.GET.get('shop')
    try:
        session = shopify.Session(shop_url, settings.API_VERSION)
        access_token = session.request_token(request.GET)
        request.session['shopify'] = {
            "shop_url": shop_url,
            "access_token": access_token
        }

    except shopify.ValidationException:
        messages.error(request, "Could not log in to Shopify store.")
        return redirect(reverse('login'))

    messages.info(request, "Logged in to shopify store.")

    request.session.pop('return_to', None)
    sync_shopify_orders.delay(shop_url, access_token)
    sync_shopify_products.delay(shop_url, access_token)
    return redirect("/admin")


def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")

    return redirect(reverse('login'))
