from django.contrib import admin

from Polling.models import Poll


class PollAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'description', 'status')


admin.site.register(Poll, PollAdmin)
