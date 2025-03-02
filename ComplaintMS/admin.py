# admin.py
from django.contrib import admin
from .models import Profile, Complaint, Grievance

class CAdmin(admin.ModelAdmin):
    list_display = ('user', 'Subject', 'Type_of_complaint', 'Description', 'Time', 'status')
    search_fields = ('user__username', 'Subject')  # Add search functionality
    list_filter = ('status', 'Type_of_complaint')  # Filter complaints by status and type

admin.site.register(Profile)
admin.site.register(Complaint, CAdmin)
admin.site.register(Grievance)
