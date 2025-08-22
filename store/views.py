from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Category, Review, Wishlist
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django import forms
from django.core.paginator import Paginator
from .models import Product
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def category(request, foo):
    foo = foo.replace('-',' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})

    except:
        messages.success(request, ("That category doesnt Exist "))
        return redirect('home')


def product(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all().order_by('-created_at')

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a rating.")
            return redirect('login')

        score = int(request.POST.get('score', 0))
        review_text = request.POST.get('review', '')
        user = request.user

        # Save or update the user's review
        review, created = Review.objects.update_or_create(
            product=product,
            user=user,
            defaults={'score': score, 'review': review_text}
        )

        messages.success(request, "Your rating has been submitted!")
        return redirect('product', pk=product.id)

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews
    })


def home(request):
    query = request.GET.get("q")  # search term
    brand = request.GET.get("brand")
    category = request.GET.get("category")

    products = Product.objects.all()

    # Search by product name
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if brand:
        products = products.filter(brand__icontains=brand)


    if category:
        products = products.filter(category__id=category)

    # Pagination (12 per page)
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    categories = Category.objects.all()  # for category dropdown

    return render(request, "home.html", {
        "products": products,
        "categories": categories
    })




def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have been logged in"))
            return redirect('home')
        else:
            messages.success(request, ("There was and error try again"))
            return redirect('login')


    else:

        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #log in user

            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have been registered successfully"))
            return redirect('home')
        else:
            messages.success(request, ("Whoops there was an error, please try again"))
            return redirect('register')

    else:


        return render(request, 'register.html', {'form': form})
    

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.remove(product)
    return redirect('wishlist')


@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    return render(request, 'wishlist.html', {'products': products})


