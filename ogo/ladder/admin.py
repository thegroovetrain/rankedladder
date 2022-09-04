from django.contrib import admin

from ladder.models import *


class LadderAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ladder, LadderAdmin)
admin.site.register(Match, LadderAdmin)
admin.site.register(Player, LadderAdmin)