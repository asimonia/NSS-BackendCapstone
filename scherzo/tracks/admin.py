from django.contrib import admin
from .models import Track, Course, Module

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug']
	prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
	model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ['title', 'track', 'created']
	list_filter = ['created', 'track']
	prepopulated_fields = {'slug': ('title',)}
	search_filter = ['title', 'overview']
	inlines = [ModuleInline]


