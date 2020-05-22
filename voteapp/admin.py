from django.contrib import admin
from .models import Poll, Option, Vote, Avatar, Tag, Comment

# Register your models here.


admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(Vote)
admin.site.register(Avatar)
admin.site.register(Tag)
admin.site.register(Comment)
