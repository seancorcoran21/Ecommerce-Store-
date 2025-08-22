from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
import stripe

from .cart import Cart
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.models import Order, Customer # make sure you have OrderItem model too
from store.forms import ShippingAddressForm

# Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def cart_summary(request):
    cart = Cart(request)
    cart_products = []
    totals = cart.cart_total()

    for item in cart:
        for _ in range(item['quantity']):
            cart_products.append(item['product'])

    return render(request, "cart_summary.html", {
        "cart_products": cart_products,
        "totals": totals
    })


def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'error': 'No product ID provided'}, status=400)

        try:
            product = get_object_or_404(Product, id=int(product_id))
            cart.add(product=product)

            cart_quantity = cart.__len__()
            return JsonResponse({'qty': cart_quantity})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_delete(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')

    if not product_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    try:
        product = get_object_or_404(Product, id=int(product_id))
        cart.delete(product)
        return JsonResponse({'success': True, 'qty': len(cart)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def cart_update(request):
    pass


def create_checkout_session(request):
    cart = Cart(request)
    line_items = []

    for item in cart:
        product = item['product']
        
        # Use sale_price if it exists and is lower than price
        if product.sale_price and product.sale_price < product.price:
            price_to_use = product.sale_price
        else:
            price_to_use = product.price

        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(price_to_use * 100),  # convert to cents
                'product_data': {
                    'name': product.name,
                },
            },
            'quantity': item['quantity'],
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/cart/shipping-details/'),
        cancel_url=request.build_absolute_uri('/cart/cancel/'),
    )

    return redirect(checkout_session.url, code=303)



@login_required
def payment_success(request):
    cart = Cart(request)

    customer, created = Customer.objects.get_or_create(
        email=request.user.email,
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
    )

    created_orders = []  # to keep track of all orders created
    for item in cart:
        order = Order.objects.create(
            product=item['product'],
            customer=customer,
            quantity=item['quantity'],
            address='',
            phone='',
            status=False
        )
        created_orders.append(order)

    cart.clear()

    # Pass the list of orders to the template
    return render(request, "payment_success.html", {"orders": created_orders})


def payment_cancel(request):
    return render(request, "payment_cancel.html")


@login_required
def purchase_history(request):
    customer = Customer.objects.get(email=request.user.email)
    orders = Order.objects.filter(customer=customer).order_by('-date')

    for order in orders:
        order.items_list = [{
            'product': order.product,
            'quantity': order.quantity,
            'price': order.product.price,
            'image': order.product.image.url if order.product.image else None
        }]

    return render(request, "purchase_history.html", {"orders": orders})


@login_required
def shipping_details(request):
    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user = request.user
            shipping.save()
            # you could link this to an order if you have an Order model
            return redirect("payment_success")  # or an order confirmation page
    else:
        form = ShippingAddressForm()
    return render(request, "shipping_details.html", {"form": form})

