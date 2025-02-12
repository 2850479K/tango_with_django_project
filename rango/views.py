from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse


def index(request):
    # Get the top 5 most liked categories
    category_list = Category.objects.order_by('-likes')[:5]

    # Get the top 5 most viewed pages
    most_viewed_pages = Page.objects.order_by('-views')[:5]

    # Ensure we pass 'boldmessage' as required by another test
    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': category_list,
        'pages': most_viewed_pages,  # This must be passed for the test to work
    }

    return render(request, 'rango/index.html', context=context_dict)



# Create your views here.
def about(request):
    # prints out whether the method is a GET or a POST
    print(request.method)
    # prints out the user name, if no one is logged in it prints `AnonymousUser`
    print(request.user)
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/rango/')
        else:
            # The supplied form contained errors -

            # just print them to the terminal.
            print(form.errors)
        # Will handle the bad form, new form, or no form supplied cases.
        # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
