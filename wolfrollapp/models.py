from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Player(models.Model):
	name = models.CharField(max_length=50)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player", null=True, blank=True)

	def __str__(self):
		return self.name


class Role(models.Model):
	score = models.IntegerField()
	title = models.CharField(max_length=40)
	description = models.CharField(max_length=400)
	alignment = models.CharField(max_length=20)
	type = models.CharField(max_length=20)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_user", null=True, blank=True)

	def __str__(self):
		return self.title


class GameParameters(models.Model):
	preferences = models.JSONField()
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_prefs", null=True, blank=True)


class RoleAssignment(models.Model):
	role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="temp_role", null=True)
	player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="temp_player", null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignment_user", null=True)
	locked = models.BooleanField(default=False)