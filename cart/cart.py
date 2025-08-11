from store.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'price': str(product.price),
                'quantity': quantity,
            }

        self.session.modified = True

    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0

        for key, value in quantities.items():
            key = int(key)  # product ID as int
            for product in products:
                if product.id == key:
                    if product.is_sale:

                        total += product.sale_price * value['quantity']
                    else:
                        total += product.price * value['quantity']

        return total



    def delete(self, product):
        """Remove a product completely from the cart."""
        product_id = str(product.id)

        if product_id in self.cart:
            if self.cart[product_id]['quantity'] > 1:
                self.cart[product_id]['quantity'] -= 1
            else:
                del self.cart[product_id]
            self.session.modified = True

    def __len__(self):
        return sum(item.get('quantity', 1) for item in self.cart.values())

    def __iter__(self):
        """Allow iteration over the cart, yielding product + quantity."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        # Map product objects to their IDs
        products_map = {str(product.id): product for product in products}

        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if product:
                yield {
                    'product': product,
                    'price': float(item['price']),
                    'quantity': item['quantity'],
                }

    def get_prods(self):
        """Returns a queryset of products in the cart."""
        return Product.objects.filter(id__in=self.cart.keys())
