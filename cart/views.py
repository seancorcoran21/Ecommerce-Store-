from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse

def cart_summary(request):
    return render(request, "cart_summary.html", {})

def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'error': 'No product ID provided'}, status=400)

        try:
            product = get_object_or_404(Product, id=int(product_id))
            cart.add(product=product)
            return JsonResponse({'Product Name: ': product.name})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_delete(request):
    pass

def cart_update(request):
    pass
