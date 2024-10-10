from django.contrib import admin

from advertisement.models import PhotoAdvertisement, Advertisement, UploadFile, ErrorFile, Complaint, ReasonOfComplaint

# Register your models here.
admin.site.register(PhotoAdvertisement)
admin.site.register(Advertisement)
admin.site.register(UploadFile)
admin.site.register(ErrorFile)
admin.site.register(Complaint)
admin.site.register(ReasonOfComplaint)
