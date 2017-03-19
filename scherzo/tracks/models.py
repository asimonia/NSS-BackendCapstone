""" 
Content is broken down into a hierarchy from
the tracks to the courses, modules, and the content

Track > Course > Module > Content

Tracks:		Level of difficulty, (1-8 Easy-Difficult)
Course: 	Pieces, scales, chords, aural test, sight reading
Module:		All the modules contained in the course
Content:	The content that is found in the modules
"""

from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForiegnKey


class Track(models.Model):
	"""Created by the admin.  These constants a teacher
	would not have access to."""
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)

	class Meta:
		ordering = ('title',)

	def __str__(self):
		return self.title


class Course(models.Model):
	"""Teachers can create new courses. These are related
	to a specific track."""
	owner = models.ForeignKey(User, related_name='courses_created')
	track = models.ForeignKey(Track, related_name='courses')
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	overview = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-created',)

	def __str__(self):
		return self.title


class Module(models.Model):
	"""Each course is comprised of several modules which
	are tailored uniquely by the teacher."""
	course = models.ForeignKey(Course, related_name='modules')
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.title


class Content(models.Model):
	"""Content found in the modules. Use a generic FK to point
	to objects of any model.
	content_type:	ForeignKey field to the ContentType model
	object_id:		PositiveIntegerField to store the PK of the related object
	item:			A GenericForeignKey field to the related object by combining
					the two previous fields
	"""
	module = models.ForeignKey(Module, related_name='contents')
	content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in':('text',
																	'video',
																	'image',
																	'file')})
	object_id = models.PositiveIntegerField()
	item = GenericForiegnKey('content_type', 'object_id')


class ItemBase(models.Model):
	"""
	Abstract model that will serve as parent to the child content types
	that will inherit the base characteristics.
	Text, File, Image, and Video
	"""
	owner = models.ForeignKey(User, related_name='%(class)s_related')
	title = models.CharField(max_length=250)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.title


class Text(ItemBase):
	content = models.TextField()


class File(ItemBase):
	file = models.FileField(upload_to='files')


class Image(ItemBase):
	file = models.FileField(upload_to='images')


class Video(ItemBase):
	url = models.URLField()