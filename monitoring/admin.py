from django.contrib import admin
from .models import Bendung, Role, CustomUser, DebitAir, Kemantren

admin.site.register(Bendung)
admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(DebitAir)
admin.site.register(Kemantren)
