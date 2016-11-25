from django.db import models

class User(models.Model):
    name = modles.CharField(max_length=255, unique=True, verbose_name=_('Username'))
    group = models.ForeignKey(Group)

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('SharedRosterGroup'))
    members = models.ManyToManyField(
        User,
        through='Membership',
        through_fields=('group', 'user'),
    )
    owners = models.ManyToManyField(
        User,
        through='Ownership',
        through_fields=('group', 'user'),
    )
    display = models.ManyToManyFiled(
        User,
        through='Display',
        through_fields=('group', 'user'),
    )

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Ownership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Display(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
