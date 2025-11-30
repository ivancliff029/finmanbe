from django.contrib import admin
from django.urls import path, include
from finances import views  # Import your views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('finances.urls')),  # API routes
    path('', views.index, name='index'),      # Frontend home page
    path('categories/', views.category_view, name="category"),
    path('budget/', views.budget_view, name="budget"),
    path('items/', views.item_view, name="item"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]