from django.contrib import admin
from .models import Tickets,Comment,Category;

@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
	list_display = ['user','name','subject','status','priority','updated','created'];

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ['user','ticket','updated'];

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name','slug'];
	prepopulated_fields = {"slug": ("name",)}

from django.contrib import admin
from .models import UserProfile

admin.site.register(UserProfile)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
