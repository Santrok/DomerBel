from django.contrib import admin
from main_page_domer.models import Complaint, ReasonOfComplaint, Publication, PublicationAdmin, Comment, \
    PhotoPublication, Help, AboutOrganization

admin.site.register(Complaint)
admin.site.register(ReasonOfComplaint)
admin.site.register(PhotoPublication)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Comment)
admin.site.register(Help)
admin.site.register(AboutOrganization)
