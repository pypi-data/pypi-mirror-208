from .models import Application, Federation
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from djangoldp_component.models import Component, Package
from rest_framework import serializers, viewsets
from rest_framework_yaml.parsers import YAMLParser
from rest_framework_yaml.renderers import YAMLRenderer


EMAIL_FROM = (getattr(settings, 'DEFAULT_FROM_EMAIL', False) or getattr(settings, 'EMAIL_HOST_USER', False))
ANSIBLE_SERVERS = set({"127.0.0.1"})


if hasattr(settings, "ANSIBLE_SERVERS"):
    ANSIBLE_SERVERS = ANSIBLE_SERVERS.union(getattr(settings, "ANSIBLE_SERVERS"))


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def format(value):
    v = value.lower()
    if v == "false":
        return False
    elif v == "true":
        return True
    else:
        return value.replace("\r\n", "\n").replace("\n\n", "\n")


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Application
        fields = ("slug", "deploy")


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Application
        fields = ("slug", "deploy")


class ApplicationDetailSerializer(serializers.HyperlinkedModelSerializer):
    def to_representation(self, obj):
        application = super().to_representation(obj)

        federation = []
        for host in application["federation"]:
            federation.append(Federation.objects.get(urlid=host).target.api_url)

        serialized = {"apps": {"hosts": {}}}
        serialized["apps"]["hosts"][application["slug"]] = {
            "graphics": {
                "client": application["client_url"],
                "canva": application["repository"],
            },
            "data": {"api": application["api_url"], "with": federation},
            "packages": [],
            "components": [],
        }

        if application["application_title"]:
            serialized["apps"]["hosts"][application["slug"]]["graphics"][
                "title"
            ] = application["application_title"]

        if application["application_logo"]:
            serialized["apps"]["hosts"][application["slug"]]["graphics"][
                "logo"
            ] = application["application_logo"]

        if len(application["graphics"]) > 0:
            for applicationGraphic in application["graphics"]:
                if applicationGraphic.obj.primary_key:
                    if (
                        applicationGraphic.obj.primary_key
                        not in serialized["apps"]["hosts"][application["slug"]][
                            "graphics"
                        ]
                    ):
                        serialized["apps"]["hosts"][application["slug"]]["graphics"][
                            applicationGraphic.obj.primary_key
                        ] = {}
                    serialized["apps"]["hosts"][application["slug"]]["graphics"][
                        applicationGraphic.obj.primary_key
                    ][applicationGraphic.obj.key] = format(applicationGraphic.obj.value)
                else:
                    serialized["apps"]["hosts"][application["slug"]]["graphics"][
                        applicationGraphic.obj.key
                    ] = format(applicationGraphic.obj.value)

        if len(application["services"]) > 0:
            serialized["apps"]["hosts"][application["slug"]]["services"] = {}
            for applicationService in application["services"]:
                if applicationService.obj.primary_key:
                    if (
                        applicationService.obj.primary_key
                        not in serialized["apps"]["hosts"][application["slug"]][
                            "services"
                        ]
                    ):
                        serialized["apps"]["hosts"][application["slug"]]["services"][
                            applicationService.obj.primary_key
                        ] = {}
                    serialized["apps"]["hosts"][application["slug"]]["services"][
                        applicationService.obj.primary_key
                    ][applicationService.obj.key] = format(applicationService.obj.value)
                else:
                    serialized["apps"]["hosts"][application["slug"]]["services"][
                        applicationService.obj.key
                    ] = format(applicationService.obj.value)

        if len(application["npms"]) > 0:
            serialized["apps"]["hosts"][application["slug"]]["npm"] = []
            for applicationNPM in application["npms"]:
                serialized["apps"]["hosts"][application["slug"]]["npm"].append(
                    {
                        "package": applicationNPM.obj.package,
                        "version": applicationNPM.obj.version,
                    }
                )

        for applicationComponent in application["components"]:
            component = Component.objects.get(id=applicationComponent.obj.component_id)
            insertComponent = {
                "type": component.name,
                "route": format(component.preferred_route),
                "parameters": {},
                "extensions": [],
            }
            if component.auto_import:
                insertComponent["experimental"] = ["routing"]
            keys = []
            for parameter in applicationComponent.obj.parameters.all():
                if parameter.key == "route":
                    insertComponent["route"] = format(parameter.value)
                else:
                    insertComponent["parameters"][parameter.key] = format(parameter.value)
                keys.append(parameter.key)
            for parameter in component.parameters.all():
                if not parameter.key in keys:
                    if parameter.key == "route":
                        insertComponent["route"] = format(parameter.default)
                    else:
                        insertComponent["parameters"][parameter.key] = format(parameter.default)
            for extensionComponent in applicationComponent.obj.extensions.all():
                extension = Component.objects.get(id=extensionComponent.component_id)
                componentExtension = {
                    "type": extension.name,
                    "route": format(component.preferred_route),
                    "parameters": {},
                }
                if extension.auto_import:
                    componentExtension["experimental"] = ["routing"]
                keys = []
                for parameter in extensionComponent.parameters.all():
                    if parameter.key == "route":
                        componentExtension["route"] = format(parameter.value)
                    else:
                        componentExtension["parameters"][parameter.key] = format(parameter.value)
                    keys.append(parameter.key)
                for parameter in extension.parameters.all():
                    if not parameter.key in keys:
                        if parameter.key == "route":
                            componentExtension["route"] = format(parameter.default)
                        else:
                            componentExtension["parameters"][parameter.key] = format(parameter.default)
                insertComponent["extensions"].append(componentExtension)
            serialized["apps"]["hosts"][application["slug"]]["components"].append(
                insertComponent
            )

        insertDependencies = []
        for applicationPackage in application["packages"]:
            package = Package.objects.get(id=applicationPackage.obj.package_id)
            insertDependency = {
                "distribution": package.distribution,
                "module": package.module,
                "parameters": {},
            }
            keys = []
            for parameter in applicationPackage.obj.parameters.all():
                if not parameter.key in keys:
                    insertDependency["parameters"][parameter.key] = format(parameter.value)
                    keys.append(parameter.key)
            for parameter in package.parameters.all():
                if not parameter.key in keys:
                    insertDependency["parameters"][parameter.key] = format(parameter.default)
            insertDependencies.append(insertDependency)
        serialized["apps"]["hosts"][application["slug"]][
            "packages"
        ] = insertDependencies

        return serialized

    class Meta:
        model = Application
        lookup_field = "slug"
        fields = [
            "urlid",
            "slug",
            "api_url",
            "client_url",
            "application_title",
            "application_logo",
            "services",
            "graphics",
            "npms",
            "components",
            "packages",
            "repository",
            "federation",
        ]
        extra_kwargs = {"url": {"lookup_field": "slug"}}


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    parser_classes = (YAMLParser,)
    renderer_classes = (YAMLRenderer,)


class ApplicationDetailViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    lookup_field = "slug"
    parser_classes = (YAMLParser,)
    renderer_classes = (YAMLRenderer,)


def mark_as_doing(request, slug):
    if request.method == "GET" and get_client_ip(request) in ANSIBLE_SERVERS:
        application = Application.objects.get(slug=slug)
        for deploy in application.deployments.filter(status="Todo"):
            deploy.status = "Doing"
            deploy.save()
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "invalid request"}, status=400)

def mark_as_done(request, slug):
    if request.method == "GET" and get_client_ip(request) in ANSIBLE_SERVERS:
        application = Application.objects.get(slug=slug)
        for deploy in application.deployments.filter(status="Doing"):
            deploy.status = "Done"
            deploy.save()
            if deploy.requester:
                message = _("Woah! Deployment done!")
                send_mail(
                    _('Déploiement de ') + application.application_title + " (https://{})".format(application.client_url),
                    message,
                    EMAIL_FROM,
                    [deploy.requester.email],
                    fail_silently=True,
                    html_message=message
                )

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "invalid request"}, status=400)


def mark_as_failed(request, slug):
    if request.method == "GET" and get_client_ip(request) in ANSIBLE_SERVERS:
        application = Application.objects.get(slug=slug)
        for deploy in application.deployments.filter(status="Doing"):
            deploy.status = "Failed"
            deploy.save()
            if deploy.requester:
                message = _("Woah! Deployment failed!")
                send_mail(
                    _('Déploiement de ') + application.application_title + " (https://{})".format(application.client_url),
                    message,
                    EMAIL_FROM,
                    [deploy.requester.email],
                    fail_silently=True,
                    html_message=message
                )

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "invalid request"}, status=400)
