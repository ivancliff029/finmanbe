from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_amount(self):
        # Fixed: use 'itemsItem' instead of 'items'
        return sum(item.amount for item in self.itemsItem.all())

class Item(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="items_added"
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='itemsItem'  # This is the related_name
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} UGX"
    
class Budget(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="budget_added"
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='itemsBudget'
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    type = models.CharField(max_length=200, default='Daily')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} UGX"