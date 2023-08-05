from django.contrib import admin

from minidebconf.models import Diet, Registration, RegistrationType, ShirtSize


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'registration_type', 'involvement', 'gender', 'country', 'diet', 'shirt_size')
    list_filter = ('registration_type', 'involvement', 'gender', 'days', 'diet', 'shirt_size')

admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegistrationType)
admin.site.register(Diet)
admin.site.register(ShirtSize)
