from django.contrib import admin

from Polling.models import Poll, User, UserPoll, PollOption


class PollAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'description', 'status')
    list_editable = ('title', 'status')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_editable = ('email', )


class UserPollAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'choices')


class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'value', 'final')


admin.site.register(Poll, PollAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserPoll, UserPollAdmin)
admin.site.register(PollOption, PollOptionAdmin)
