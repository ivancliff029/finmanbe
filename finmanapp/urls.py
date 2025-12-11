from django.contrib import admin
from django.urls import path, include
from finances import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('finances.urls')),  
    
    path('', views.index, name='index'),      
    path('categories/', views.category_view, name="category"),
    path('budget/', views.budget_view, name="budget"),
    path('items/', views.item_view, name="item"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('to-buy/', views.to_buy_view, name='to-buy'),
    path('to-buy/delete/<int:pk>/', views.delete_to_buy, name='delete-to-buy'),
]