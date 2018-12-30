from django.contrib import admin

from Polling.models import Poll, User, UserPoll, NormalPollOption, WeeklyPollOption


class PollAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'description', 'status', 'is_normal')
    list_editable = ('title', 'status')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_editable = ('email', )


class UserPollAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'choices')


class NormalPollOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'value', 'final')


class WeeklyPollOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'weekday', 'start_time', 'end_time', 'final')


admin.site.register(Poll, PollAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserPoll, UserPollAdmin)
admin.site.register(NormalPollOption, NormalPollOptionAdmin)
admin.site.register(WeeklyPollOption, WeeklyPollOptionAdmin)
