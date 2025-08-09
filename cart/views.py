from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

def cart_summary(request):
    cart = Cart(request)
    cart_products = []

    for item in cart:
        for _ in range(item['quantity']):
            cart_products.append(item['product'])

    return render(request, "cart_summary.html", {"cart_products": cart_products})


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
            #return JsonResponse({'Product Name: ': product.name})
            
            return JsonResponse({'qty': cart_quantity})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_delete(request):
    pass

def cart_update(request):
    pass
