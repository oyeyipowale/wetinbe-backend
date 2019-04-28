from django.db import models
import uuid as uuid_lib
from django.urls import reverse
from django.core.validators import RegexValidator
from ..wetinbe.models import TimeStampedModel


def upload_location(instance, filename):
    return f"{instance.name}/{filename}"


def service_img_upload_location(instance, filename):
    return f"services/{instance.provider}/{filename}"


class Provider(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to=upload_location,
                              blank=True,
                              height_field="height_field",
                              width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    uuid = models.UUIDField(db_index=True,
                            default=uuid_lib.uuid4,
                            editable=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    provider = models.ForeignKey(Provider,
                                 related_name='services',
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, null=True)
    cover_img = models.ImageField(upload_to=service_img_upload_location,
                                  blank=True,
                                  height_field="height_field",
                                  width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    overview = models.CharField(max_length=280, blank=True)
    body = models.TextField(blank=True)
    uuid = models.UUIDField(db_index=True,
                            default=uuid_lib.uuid4,
                            editable=False)
    has_shortcode = models.BooleanField(default=False)
    has_textcode = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Post save - do something

        # save
        super().save(*args, **kwargs)

        # pre save - do something
        if self.has_shortcode:
            ShortCode.objects.get_or_create(service=self)
        if self.has_textcode:
            TextCode.objects.get_or_create(service=self)


class TextCode(TimeStampedModel):
    service = models.OneToOneField(
        Service, on_delete=models.CASCADE, primary_key=True, related_name="textcode")
    textcode_regex = RegexValidator(
        regex=r'^\d{3,10}$',
        message=(
            'Only number is allowed -- min of 3 and max of 10; no text please'
        ),
    )
    textcode = models.CharField(max_length=10, validators=[
                                textcode_regex], blank=True)
    message = models.CharField(max_length=10, blank=True)

    def __str__(self):
        provider = self.service.provider
        topic = self.service.title[:10]
        result = f"code {self.textcode} for {topic} under {provider}"
        return result


class ShortCode(TimeStampedModel):
    service = models.OneToOneField(
        Service, on_delete=models.CASCADE, primary_key=True, related_name="shortcode")
    shortcode = models.CharField()

    def __str__(self):
        provider = self.service.provider
        topic = self.service.title[:10]
        result = f"code {self.shortcode} for {topic} under {provider}"
        return result
