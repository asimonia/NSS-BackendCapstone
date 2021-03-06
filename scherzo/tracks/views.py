from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Count


from .forms import ModuleFormSet
from .models import Course, Module, Content, Track
from students.forms import CourseEnrollForm
from django.core.cache import cache


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


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
	fields = ['track', 'title', 'slug', 'overview']
	success_url = reverse_lazy('manage_course_list')
	template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
	template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
	permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
	permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
	template_name = 'courses/manage/course/delete.html'
	success_url = reverse_lazy('manage_course_list')
	permission_required = 'courses.delete_course'
	

class CourseModuleUpdateView(TemplateResponseMixin, View):
	template_name = 'courses/manage/module/formset.html'
	course = None

	def get_formset(self, data=None):
		return ModuleFormSet(instance=self.course, data=data)

	def dispatch(self, request, pk):
		self.course = get_object_or_404(Course, id=pk, owner=request.user)
		return super().dispatch(request, pk)

	def get(self, request, *args, **kwargs):
		formset = self.get_formset()
		return self.render_to_response({'course': self.course, 'formset': formset})

	def post(self, request, *args, **kwargs):
		formset = self.get_formset(data=request.POST)
		if formset.is_valid():
			formset.save()
			return redirect('manage_course_list')
		return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
	module = None
	model = None
	obj = None
	template_name = 'courses/manage/content/form.html'

	def get_model(self, model_name):
		"""Check the given model name is one of the four content models:
		text, video, image, or file.  Use apps module to obtain the actual
		class for the given model name.
		"""
		if model_name in ['text', 'video', 'image', 'file']:
			return apps.get_model(app_label='courses', model_name=model_name)
		return None

	def get_form(self, model, *args, **kwargs):
		"""Build a dynamic form and exclude the specified files"""
		Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
		return Form(*args, **kwargs)

	def dispatch(self, request, module_id, model_name, id=None):
		"""Receives the URL parameters and stores the module, model and content
		object as class attributes"""
		self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
		self.model = self.get_model(model_name)
		if id:
			self.obj = get_object_or_404(self.model, id=id, owner=request.user)
		return super().dispatch(request, module_id, model_name, id)

	def get(self, request, module_id, model_name, id=None):
		"""Executed when a GET request is received.  We build the model
		for the Text, Video, Image, or File instance being updated.
		"""
		form = self.get_form(self.model, instance=self.obj)
		return self.render_to_response({'form': form, 'object': self.obj})

	def post(self, request, module_id, model_name, id=None):
		"""Executed when POST request is received.  We build the modelform
		passing any submitted data and files to it.  Then we validate it.
		"""
		form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.owner = request.user
			obj.save()
			if not id:
				# new content
				Content.objects.create(module=self.module, item=obj)
			return redirect('module_content_list', self.module.id)
		return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
	"""Retrieves the Content object with the given id,
	deletes the related Text, Video, Image or File object
	deletes the Content object
	"""
	def post(self, request, id):
		content = get_object_or_404(Content, id=id, module__course__owner=request.user)
		module = content.module
		content.item.delete()
		return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
	"""View to display all modules for a course and list
	list contents for a specific module.
	"""
	template_name = 'courses/manage/module/content_list.html'

	def get(self, request, module_id):
		module = get_object_or_404(Module, id=module_id, course__owner=request.user)
		return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	"""Reorder modules based on the DnD interface"""
	def post(self, request):
		for id, order in self.request_json.items():
			Module.objects.filter(id=id, course__owner=request.user).update(order=order)
		return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	"""Reorder contents based on the DnD interface"""
	def post(self, request):
		for id, order in self.request_json.items():
			Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
		return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
	"""List all available courses, filtered by track.
	Display a single course overview.
	Get all tracks, including the total number of courses for each.
	Use the annotate() method with Count() aggregation.
	Get all available courses, including the total number of modules contained in each course.
	"""
	model = Course
	template_name = 'courses/course/list.html'

	def get(self, request, track=None):
		tracks = cache.get('all_tracks')
		if not tracks:
			tracks = Track.objects.annotate(total_courses=Count('courses'))
			cache.set('all_tracks', tracks)	
		all_courses = Course.objects.annotate(total_modules=Count('modules'))
		if track:
			track = get_object_or_404(Track, slug=track)
			key = 'track_{}_courses'.format(track.id)
			courses = cache.get(key)
			if not courses:
				courses = courses.filter(track=track)
				cache.set(key, courses)
		else:
			courses = cache.get('all_courses')
			if not courses:
				courses = all_courses
				cache.set('all_courses', courses)
		return self.render_to_response({'tracks': tracks,
										'track': track,
										'courses': courses})

class CourseDetailView(DetailView):
	model = Course
	template_name = 'courses/course/detail.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
		return context