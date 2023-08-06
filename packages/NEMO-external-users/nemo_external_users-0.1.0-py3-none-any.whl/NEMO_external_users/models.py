from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from NEMO.models import User as NemoUser
from NEMO.models import Project, Tool, ToolQualificationGroup


class ExternalUserAttributes(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class ExternalUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        normalized_email = self.normalize_email(email)

        user = self.create_user(
            email=normalized_email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.is_admin = True
        user.save(using=self._db)
        return user


class ExternalUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    nemo_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
    )

    objects = ExternalUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def settings_handler(instance):
    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_PROJECTS'):
        for project_name in settings.NEMO_EXTERNAL_USERS_NEW_USER_PROJECTS:
            instance.nemo_user.projects.add(Project.objects.filter(name=project_name).first())

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_TOOLS'):
         for tool_name in settings.NEMO_EXTERNAL_USERS_NEW_USER_TOOLS:
             tool = Tool.objects.filter(name=tool_name).first()
             if tool:
                 tool.user_set.add(instance.nemo_user.id)

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_TOOL_QUALIFICATION_GROUPS'):
        for group_name in settings.NEMO_EXTERNAL_USERS_NEW_USER_TOOL_QUALIFICATION_GROUPS:
            try:
                tools = ToolQualificationGroup.objects.filter(name=group_name).first().tools.all()
            except AttributeError as e:
                print(f"Tools qualification group '{group_name}' doesn't exist")
                continue

            for tool in tools:
                tool.user_set.add(instance.nemo_user.id)

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_STAFF'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_STAFF:
            instance.nemo_user.is_staff = True
        else:
            instance.nemo_user.is_staff = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_USER_OFFICE'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_USER_OFFICE:
            instance.nemo_user.is_user_office = True
        else:
            instance.nemo_user.is_user_office = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_ACCOUNTING_OFFICER'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_ACCOUNTING_OFFICER:
            instance.nemo_user.is_accounting_officer = True
        else:
            instance.nemo_user.is_accounting_officer = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_FACILITY_MANAGER'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_FACILITY_MANAGER:
            instance.nemo_user.is_facility_manager = True
        else:
            instance.nemo_user.is_facility_manager = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_ADMINISTRATOR'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_ADMINISTRATOR:
            instance.nemo_user.is_superuser = True
        else:
            instance.nemo_user.is_superuser = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_TECHNICIAN'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_TECHNICIAN:
            instance.nemo_user.is_technician = True
        else:
            instance.nemo_user.is_technician = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_IS_SERVICE_PERSONNEL'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_IS_SERVICE_PERSONNEL:
            instance.nemo_user.is_service_personnel = True
        else:
            instance.nemo_user.is_service_personnel = False

    if hasattr(settings, 'NEMO_EXTERNAL_USERS_NEW_USER_TRAINING_REQUIRED'):
        if settings.NEMO_EXTERNAL_USERS_NEW_USER_TRAINING_REQUIRED:
            instance.nemo_user.training_required = True
        else:
            instance.nemo_user.training_required = False

    return instance

@receiver(post_save, sender=ExternalUser)
def create_related_nemo_user(sender, instance, **kwargs):
    if instance.is_active and instance.nemo_user is None:
        instance.nemo_user = NemoUser.objects.create_user(
            username=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
        )
        instance = settings_handler(instance)
        instance.nemo_user.is_active = instance.is_active
        instance.nemo_user.save()
        instance.save()


@receiver(post_delete, sender=ExternalUser)
def delete_related_nemo_user(sender, instance, **kwargs):
    try:
        nemo_user = instance.nemo_user
    except NemoUser.DoesNotExist:
        nemo_user = None

    if instance.is_active and nemo_user is not None:
        instance.nemo_user.is_active = False
        instance.nemo_user.save()
        instance.nemo_user.delete()


@receiver(post_delete, sender=NemoUser)
def delete_related_external_user(sender, instance, **kwargs):
    try:
        external_user = instance.externaluser
    except ExternalUser.DoesNotExist:
        external_user = None

    if instance.is_active and external_user is not None:
        instance.externaluser.is_active = False
        instance.externaluser.save()
        instance.externaluser.delete()
