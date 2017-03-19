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


