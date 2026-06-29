from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Auto-create a Customer whenever a new User is created
    @receiver(post_save, sender=User)
    def create_customer(sender, instance, created, **kwargs):
        if created:
            Customer.objects.create(user=instance)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    order_number = models.CharField(max_length=50, unique=True)  # e.g. ORD-789
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number} - {self.customer.name} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price per unit

    def __str__(self):
        return f"{self.product_name} x{self.quantity} (Order: {self.order.order_number})"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("failed", "Failed Delivery"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipment"
    )
    tracking_number = models.CharField(max_length=100, unique=True)
    carrier = models.CharField(max_length=100)  # e.g. FedEx, UPS, DHL
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    shipped_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number} - {self.tracking_number}"


class CancellationRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    REASON_CHOICES = [
        ("changed_mind", "Changed My Mind"),
        ("wrong_item", "Ordered Wrong Item"),
        ("found_better_price", "Found Better Price"),
        ("delay", "Delivery Too Slow"),
        ("other", "Other"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="cancellation"
    )
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="requested"
    )
    notes = models.TextField(blank=True, null=True)  # customer's extra explanation
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Cancellation for {self.order.order_number} ({self.status})"


class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("refunded", "Refunded"),
    ]

    REASON_CHOICES = [
        ("wrong_item", "Wrong Item Received"),
        ("damaged", "Item Damaged"),
        ("not_as_described", "Not as Described"),
        ("changed_mind", "Changed My Mind"),
        ("other", "Other"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="return_request"
    )
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="requested"
    )
    notes = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    refunded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Return for {self.order.order_number} ({self.status})"