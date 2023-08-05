from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from djangoldp_component.models import Component, Package
from djangoldp.models import Model
from rest_framework.exceptions import ValidationError
import uuid


class Application(Model):
    repository = models.CharField(max_length=255, blank=True, null=True)
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    creator = models.ForeignKey(
        get_user_model(),
        related_name="applications",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    api_url = models.CharField(
        max_length=255, blank=True, null=True, help_text='Without "http(s)://"'
    )
    client_url = models.CharField(
        max_length=255, blank=True, null=True, help_text='Without "http(s)://"'
    )
    # May move appliation_* to graphics?
    application_title = models.CharField(max_length=255, blank=True, null=True)
    application_logo = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    @property
    def deploy(self):
        return self.deployments.filter(status="Todo").count() > 0

    def __str__(self):
        try:
            return "{} ({})".format(self.friendly_name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        auto_author = "creator"
        container_path = "/applications/"
        depth = 1  # Do not serialize user
        lookup_field = "slug"
        nested_fields = ["components", "packages"]
        ordering = ["slug"]
        owner_field = "creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "friendly_name": "sib:friendlyName",
            "short_description": "sib:shortDescription",
            "creator": "foaf:user",
        }
        rdf_type = "sib:application"
        serializer_fields = [
            "@id",
            "repository",
            "friendly_name",
            "short_description",
            "creator",
            "api_url",
            "client_url",
            "application_title",
            "application_logo",
            "components",
            "packages",
            "graphics",
            "services",
            "federation",
        ]
        superuser_perms = ["view"]
        verbose_name = _("application")
        verbose_name_plural = _("applications")


STATUS_CHOICES = [
    ("Todo", _("Todo")),
    ("Doing", _("Doing")),
    ("Done", _("Done")),
    ("Failed", _("Failed")),
]


class Deployment(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="deployments",
        null=True,
        blank=True,
    )
    requester = models.ForeignKey(
        get_user_model(),
        related_name="deployments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Request date")
    resolutionDate = models.DateTimeField(auto_now=True, verbose_name="Resolution date")
    status = models.CharField(
        max_length=8, choices=STATUS_CHOICES, default="Todo", null=True, blank=True
    )

    def __str__(self):
        try:
            return "{} - {} ({})".format(
                self.date, self.application.friendly_name, self.application.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        container_path = "/deployments/"
        depth = 0
        auto_author = "requester"
        owner_field = "requester"
        owner_perms = ["inherit", "change", "delete"]
        ordering = ["application__urlid", "date"]
        rdf_context = {
            "application": "sib:application",
            "date": "sib:deploymentDate",
            "resolutionDate": "sib:deploymentDate",
            "status": "sib:deploymentStatus",
        }
        rdf_type = "sib:federation"
        serializer_fields = [
            "@id",
            "date",
            "resolutionDate",
            "status",
        ]
        superuser_perms = ["view"]
        verbose_name = _("deployment")
        verbose_name_plural = _("deployments")


class Federation(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="federation",
        null=True,
        blank=True,
    )
    target = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="targeted_federation",
        null=True,
        blank=True,
    )

    def __str__(self):
        try:
            return "{} ({})".format(self.friendly_name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        container_path = "/federations/"
        depth = 0
        # nested_fields = []
        ordering = ["application__urlid", "target__urlid"]
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "target": "sib:application",
        }
        rdf_type = "sib:federation"
        serializer_fields = [
            "@id",
            "target",
        ]
        superuser_perms = ["view"]
        verbose_name = _("federation")
        verbose_name_plural = _("federations")


class ApplicationGraphics(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="graphics",
        null=True,
        blank=True,
    )
    primary_key = models.CharField(max_length=255, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return "{} + {}.{} ({})".format(
                self.application.friendly_name, self.primary_key, self.key, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-graphics/"
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "primary_key": "sib:key",
            "key": "sib:key",
            "value": "sib:value",
        }
        rdf_type = "sib:graphic"
        serializer_fields = ["@id", "primary_key", "key", "value"]
        superuser_perms = ["inherit"]
        verbose_name = _("application graphic")
        verbose_name_plural = _("application graphics")


class ApplicationService(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="services",
        null=True,
        blank=True,
    )
    primary_key = models.CharField(max_length=255, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return "{} + {}.{} ({})".format(
                self.application.friendly_name, self.primary_key, self.key, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-services/"
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "primary_key": "sib:key",
            "key": "sib:key",
            "value": "sib:value",
        }
        rdf_type = "sib:service"
        serializer_fields = ["@id", "primary_key", "key", "value"]
        superuser_perms = ["inherit"]
        verbose_name = _("application service")
        verbose_name_plural = _("application services")


class ApplicationNPM(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="npms",
        null=True,
        blank=True,
    )
    package = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} + {}@{} ({})".format(
                self.application.friendly_name, self.package, self.version, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-npms/"
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "package": "sib:npmpackage",
            "version": "sib:npmversion",
        }
        rdf_type = "sib:npm"
        serializer_fields = ["@id", "package", "version"]
        superuser_perms = ["inherit"]
        verbose_name = _("application npm")
        verbose_name_plural = _("application npms")


class ApplicationComponent(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="components",
        null=True,
        blank=True,
    )
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="applications",
        null=True,
        blank=True,
    )

    def __str__(self):
        try:
            return "{} + {} ({})".format(
                self.application.friendly_name, self.component.friendly_name, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-components/"
        nested_fields = ["component", "parameters"]
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "component": "sib:component",
        }
        rdf_type = "sib:dependency"
        serializer_fields = ["@id", "component", "parameters"]
        superuser_perms = ["inherit"]
        verbose_name = _("application component")
        verbose_name_plural = _("application components")

    def save(self, *args, **kwargs):
        if (
            not self.pk
            and ApplicationComponent.objects.filter(
                component=self.component, application=self.application
            ).exists()
        ):
            return

        super(ApplicationComponent, self).save(*args, **kwargs)


class ApplicationComponentParameter(Model):
    component = models.ForeignKey(
        ApplicationComponent,
        on_delete=models.CASCADE,
        related_name="parameters",
        null=True,
        blank=True,
    )
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} -> {} ({})".format(
                self.component.application.friendly_name,
                self.component.component.friendly_name,
                self.urlid,
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-component-parameters/"
        owner_field = "component__application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "component": "sib:dependency",
            "key": "sib:key",
            "value": "sib:value",
        }
        rdf_type = "sib:parameter"
        serializer_fields = ["@id", "key", "value"]
        superuser_perms = ["inherit"]
        verbose_name = _("component parameter")
        verbose_name_plural = _("component parameters")


class ApplicationPackage(Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="packages",
        null=True,
        blank=True,
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="applications",
        null=True,
        blank=True,
    )

    def __str__(self):
        try:
            return "{} + {} ({})".format(
                self.application.friendly_name, self.package.friendly_name, self.urlid
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-packages/"
        nested_fields = ["package", "parameters"]
        owner_field = "application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "application": "sib:application",
            "package": "sib:package",
        }
        rdf_type = "sib:dependency"
        serializer_fields = ["@id", "package", "parameters"]
        superuser_perms = ["inherit"]
        verbose_name = _("application package")
        verbose_name_plural = _("application packages")

    def save(self, *args, **kwargs):
        if (
            not self.pk
            and ApplicationPackage.objects.filter(
                package=self.package, application=self.application
            ).exists()
        ):
            return

        super(ApplicationPackage, self).save(*args, **kwargs)


class ApplicationPackageParameter(Model):
    package = models.ForeignKey(
        ApplicationPackage,
        on_delete=models.CASCADE,
        related_name="parameters",
        null=True,
        blank=True,
    )
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} -> {} ({})".format(
                self.package.application.friendly_name,
                self.package.package.friendly_name,
                self.urlid,
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "application-package-parameters/"
        owner_field = "package__application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "package": "sib:dependency",
            "key": "sib:key",
            "value": "sib:value",
        }
        rdf_type = "sib:parameter"
        serializer_fields = ["@id", "key", "value"]
        superuser_perms = ["inherit"]
        verbose_name = _("package parameter")
        verbose_name_plural = _("package parameters")


class ComponentExtension(Model):
    base_component = models.ForeignKey(
        ApplicationComponent,
        on_delete=models.CASCADE,
        related_name="extensions",
        null=True,
        blank=True,
    )
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="extends",
        null=True,
        blank=True,
    )

    def __str__(self):
        try:
            return "{} + {} ({})".format(
                self.base_component.application.friendly_name,
                self.component.friendly_name,
                self.urlid,
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "component-extensions/"
        nested_fields = ["component", "base_component"]
        owner_field = "base_component__application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "base_component": "sib:dependency",
            "component": "sib:component",
        }
        rdf_type = "sib:dependency"
        serializer_fields = ["@id", "component"]
        superuser_perms = ["inherit"]
        verbose_name = _("component extension")
        verbose_name_plural = _("component extensions")

    def save(self, *args, **kwargs):
        if (
            not self.pk
            and ComponentExtension.objects.filter(
                base_component=self.base_component, component=self.component
            ).exists()
        ):
            return

        super(ComponentExtension, self).save(*args, **kwargs)


class ComponentExtensionParameter(Model):
    component = models.ForeignKey(
        ComponentExtension,
        on_delete=models.CASCADE,
        related_name="parameters",
        null=True,
        blank=True,
    )
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return "{} -> {} ({})".format(
                self.component.base_component.application.friendly_name,
                self.component.component.friendly_name,
                self.urlid,
            )
        except:
            return self.urlid

    class Meta(Model.Meta):
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit"]
        container_path = "component-extension-parameters/"
        owner_field = "component__base_component__application__creator"
        owner_perms = ["inherit", "change", "delete"]
        rdf_context = {
            "component": "sib:dependency",
            "key": "sib:key",
            "value": "sib:value",
        }
        rdf_type = "sib:parameter"
        serializer_fields = ["@id", "key", "value"]
        superuser_perms = ["inherit"]
        verbose_name = _("component extension parameter")
        verbose_name_plural = _("component extension parameters")


@receiver(pre_save, sender=Application)
def pre_save_slugify(sender, instance, **kwargs):
    if not instance.urlid or instance.urlid.startswith(settings.SITE_URL):
        if getattr(instance, Model.slug_field(instance)) != slugify(
            instance.friendly_name
        ):
            if (
                sender.objects.local()
                .filter(slug=slugify(instance.friendly_name))
                .count()
                > 0
            ):
                raise ValidationError(sender.__name__ + str(_(" must be unique")))
            setattr(
                instance, Model.slug_field(instance), slugify(instance.friendly_name)
            )
            setattr(instance, "urlid", "")
    else:
        # Is a distant object, generate a random slug
        setattr(instance, Model.slug_field(instance), uuid.uuid4().hex.upper()[0:8])
