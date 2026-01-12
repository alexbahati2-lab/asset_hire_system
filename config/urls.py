from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from rentals.views import c2b_callback

# ----------------------
# Admin Branding
# ----------------------
admin.site.site_header = "Asset Hire Management System"
admin.site.site_title = "Asset Hire Admin"
admin.site.index_title = "Asset Management Dashboard"

# ----------------------
# Views
# ----------------------
def root_redirect(request):
    """Redirect root URL to admin"""
    return redirect('/admin/')

# ----------------------
# URL Patterns
# ----------------------
urlpatterns = [
    path('', root_redirect),                  # Root redirect to admin
    path('admin/', admin.site.urls),          # Django admin
    path('mpesa/c2b/callback/', c2b_callback),  # M-Pesa callback
]
