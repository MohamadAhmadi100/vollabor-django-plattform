from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from comment.models import Comment
from django.urls import reverse

# My managers
class LikeManager(models.Manager):
	def Active(self):
		return self.filter(status='true')

class CategoryManager(models.Manager):
	def Active(self):
		return self.filter(status=True)

class TopicManager(models.Manager):
	def Published(self):
		return self.filter(deleted=False)

# Create your models here.
STATUS_CHOICES = (
    ('true', 'True'),
    ('false', 'False'),
)


#ForumRole
class ForumRole(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

	create_category_subcategory = models.BooleanField(default=False, null=True, verbose_name="Create category, sub category")
	delete_category_subcategory = models.BooleanField(default=False, null=True, verbose_name="Delete category, sub category")
	edit_category_subcategory = models.BooleanField(default=False, null=True, verbose_name="Edit category, sub category")

	delete_topic = models.BooleanField(default=False, null=True, verbose_name="Delete topic")

	delete_comment_replycomment = models.BooleanField(default=False, null=True, verbose_name="Delete comment, reply comment")
	
	is_staff = models.BooleanField(default=False, null=True, verbose_name="Is staff")
	
	def __str__(self):
	    return self.user.get_full_name()

class MainCategory(models.Model):
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=200, unique=True)
	description = models.TextField(blank=True)
	img = models.ImageField(null=True, max_length=100)
	status = models.BooleanField(default=True, verbose_name='To be displayed?')

	def __str__(self):
		return self.title


class Category(models.Model):
	sub_category =  models.ForeignKey(MainCategory, default=None, null=True, blank=True, on_delete=models.CASCADE, related_name='childern')
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=200, unique=True)
	description = models.TextField()
	img = models.ImageField(null=True, max_length=100)
	status = models.BooleanField(default=True, verbose_name='To be displayed?')
	workshop_and_research = models.BooleanField(default=False, verbose_name='Work shop adn research?')

	def __str__(self):
		return self.title
	objects = CategoryManager()


class Postes(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, verbose_name="Title")
	# deleted
	# description = models.TextField(verbose_name="Description")
	deleted = models.BooleanField(null=True, default=False)
	categorys = models.ForeignKey(Category, null=True, on_delete=models.CASCADE, related_name='postes')
	created = models.DateTimeField(auto_now_add=True)

	# deleted
	# img = models.ImageField(null=True, verbose_name='Upload img')
	class Meta:
		ordering = ['-created']
	objects = TopicManager()

	@property
	def num_likeds(self):
		return self.liked.all().count()
		
	def get_absolute_url(self):
		return reverse('forum:post-recent')


	
class History(models.Model):
	user = models.IntegerField(default=0)
	topic = models.ForeignKey(Postes, null=True, on_delete=models.CASCADE, related_name='topic_history')
	date_add_to_history = models.DateTimeField(auto_now_add=True)


class TopicComment(models.Model):
	user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	topic =  models.ForeignKey(Postes, on_delete=models.CASCADE, null=True, related_name='comment_t')
	description = models.TextField()
	# like = models.IntegerField(null=True, default=0)
	# disslike = models.IntegerField(null=True, default=0)
	id_comments = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return self.description

class ReplyComment(models.Model):
	user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='rep_comment')
	#create new
	topic =  models.ForeignKey(Postes, on_delete=models.CASCADE, null=True, related_name='reply_comment_t')
	reply_comment = models.TextField()
	# like = models.IntegerField(null=True, default=0)
	# disslike = models.IntegerField(null=True, default=0)
	comment_int = models.IntegerField(default=None, null=True)
	created = models.DateTimeField(auto_now_add=True, null=True)
	def __str__(self):
		return self.reply_comment


class Like(models.Model):
	user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='like_user')
	topic =  models.ForeignKey(Postes, on_delete=models.CASCADE, blank=True, null=True, related_name='like_topic')
	comment =  models.ForeignKey(TopicComment, on_delete=models.CASCADE, blank=True, null=True, related_name='like_comment')
	replycomment =  models.ForeignKey(ReplyComment, on_delete=models.CASCADE, blank=True, null=True, related_name='like_replycomment')
	status = models.CharField(max_length=50, default='true', null=True, choices=STATUS_CHOICES)
	created = models.DateTimeField(auto_now_add=True, null=True)
	objects = LikeManager()


class DisLike(models.Model):
	user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='dislike_user')
	# topic =  models.ForeignKey(Postes, on_delete=models.CASCADE, null=True, related_name='dislike_topic')
	comment =  models.ForeignKey(TopicComment, on_delete=models.CASCADE, null=True, related_name='dislike_comment')
	replycomment =  models.ForeignKey(ReplyComment, on_delete=models.CASCADE, null=True, related_name='dislike_replycomment')
	status = models.CharField(max_length=50, default='true', null=True, choices=STATUS_CHOICES)
	created = models.DateTimeField(auto_now_add=True, null=True)
	objects = LikeManager()


class ViewTopic(models.Model):
	user =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='view_user')
	topic =  models.ForeignKey(Postes, on_delete=models.CASCADE, null=True, related_name='view_topic')
	created = models.DateTimeField(auto_now_add=True, null=True)
