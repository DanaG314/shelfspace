from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
    related_name='main_app')
    STATUS_CHOICES = [
        ('reading', 'Reading'),
        ('completed', 'Completed'),
        ('plan_to_read', 'Plan to Read'),
    ]

    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]

    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    cover_url = models.URLField(blank=True, null=True)
    isbn13 = models.CharField(max_length=13, blank=True, null=True)
    total_pages = models.IntegerField(default=0)
    current_page = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plan_to_read')
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property 
    def progress(self):
        if self.total_pages ==0:
            return 0
        return int((self.current_page / self.total_pages) *100)

class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=200)
    book_title = models.CharField(max_length=500, blank=True, null=True)
    date_shown = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:50]}... - {self.author}"
