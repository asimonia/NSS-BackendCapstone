from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Course


class OwnerMixin:

	def get_queryset(self):
		qs = super().get_queryset()
		return qs.filter(owner=self.request.user)


class OwnerEditMixin:

	def form_valid(self, form):
		form.instance.owner = self.request.user
		return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
	model = Course
	fields = ['track', 'title', 'slug', 'overview']
	success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
	fields = ['track', 'title', 'slug', 'overview']
	success_url = reverse_lazy('manage_course_list')
	template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
	template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
	permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
	template_name = 'courses/manage/course/form.html'
	permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
	template_name = 'courses/manage/course/delete.html'
	success_url = reverse_lazy('manage_course_list')
	permission_required = 'courses.delete_course'
	



