from django.db import models


class Base(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=False)
    deleted_at = models.DateTimeField(null=True, default=None)

    class Meta:
        abstract = True        