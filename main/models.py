from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates')
    div = models.CharField(choices=[
        ('BE', 'Backend'),
        ('CSC', 'Corporate Supply Chain'),
        ('EWM', 'Enhanced Warehouse Management'),
        ('FE', 'Frontend'),
        ('PROC', 'Procurement'),
        ('QM', 'Quality Management'),
        ('ATV', 'Automotive'),
        ('CSS', 'Connected Secure Systems'),
        ('GIP', 'Green Industrial Power'),
        ('PSS', 'Power & Sensor Systems'),
    ], max_length=10, default='FE')
    sub_div = models.CharField(choices=[
        ('FE VIH', 'Villach'),
        ('FE DRS', 'Dresden'),
        ('FE RBG', 'Regensburg'),
        ('FE KLM', 'Kulim'),
        ('FE QM', 'Quality Management'),
        ('FE T', 'T'),
        ('QM DI', 'DI'),
        ('QM PMT', 'PMT'),
        ('QM S', 'S'),
        ('QM SW', 'SW'),
        ('QM BE', 'Backend'),
        ('QM FE', 'Frontend'),
        ('QM GIP', 'Green Industrial Power'),
        ('QM JP', 'JP'),
        ('QM GC', 'GC'),
        ('QM AP', 'AP'),
    ], max_length=10, default='DRS')
    level = models.IntegerField(choices=[
        (1, 'Level 1 (Admin)'),
        (2, 'Level 2 (DIV Manager)'),
        (3, 'Level 3 (SUB DIV Manager)'),
        (4, 'Level 4 (Writer)'),
    ], default=4)  # Default level is 4 (Writer)

    def save(self, *args, **kwargs):
        # Ensure sub_div is only set for FE and QM divisions
        if self.div not in ['FE', 'QM']:
            self.sub_div = 'none'  # Reset sub_div to 'none' if not in FE or QM
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} {self.div} - {self.sub_div} (Level {self.level})"


# Signal to handle Profile creation and updates
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a Profile when a new User is created
        Profile.objects.create(user=instance)
    else:
        # Save the Profile when the User is updated
        instance.profile.save()


class Level4Text(models.Model):
    CATEGORY_CHOICES = [
        ('highlight', 'Highlight'),
        ('lowlight', 'Lowlight'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track the user who created the text
    sub_div = models.CharField(max_length=10, default="none")  # Subdivision
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="Highlight")  # Highlight or Lowlight
    text = models.TextField()  # Field to store the submitted text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the text was created

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.created_at}"