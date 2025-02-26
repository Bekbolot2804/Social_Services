from django.contrib import admin
from .models import Help, Lesion, Help_lesion

admin.site.register(Help)
admin.site.register(Lesion)
admin.site.register(Help_lesion)