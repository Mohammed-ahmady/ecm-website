# C:\Users\Mohammed\Documents\ECM\parts\views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView # Make sure TemplateView is imported
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Part, Category, TruckModel, Inquiry, Cart
from .forms import InquiryForm # Import the form you just created



def add_to_cart(request, part_id):
    cart = Cart(request)
    part = get_object_or_404(Part, id=part_id)
    cart.add(part=part)
    return redirect("parts:cart_detail")

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})


# View for listing parts with search and filters
class PartListView(ListView):
    model = Part
    template_name = 'parts/part_list.html' # This template needs to be created
    context_object_name = 'parts'
    paginate_by = 12 # Show 12 parts per page

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True) # Assuming 'is_active' field on Part
        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        truck_model_slug = self.request.GET.get('truck_model')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(part_number__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(truck_models__name__icontains=query)
            ).distinct() # Use .distinct() to avoid duplicate results if a part matches multiple criteria

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        if truck_model_slug:
            queryset = queryset.filter(truck_models__slug=truck_model_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['truck_models'] = TruckModel.objects.all().order_by('name')
        context['current_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_truck_model'] = self.request.GET.get('truck_model', '')
        return context

# View for a single part's details
class PartDetailView(DetailView):
    model = Part
    template_name = 'parts/part_detail.html'
    context_object_name = 'part'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Ensure only active parts are viewable
        return super().get_queryset().filter(is_active=True)

# View for the inquiry form
class InquiryCreateView(CreateView):
    model = Inquiry
    form_class = InquiryForm
    template_name = 'inquiry.html' # This will be a project-level template
    success_url = reverse_lazy('inquiry') # Redirect back to the same page or a dedicated success page

    def form_valid(self, form):
        messages.success(self.request, "Your inquiry has been submitted successfully! We will get back to you shortly.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please correct the highlighted fields.")
        return super().form_invalid(form)

# Function-based view for the home page (can be replaced by TemplateView)
def home_view(request):
    # You might want to display some featured parts or categories here
    featured_parts = Part.objects.filter(is_active=True).order_by('-created_at')[:6] # Example: show 6 active parts
    return render(request, 'home.html', {'featured_parts': featured_parts})