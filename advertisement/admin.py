from django.contrib import admin

from advertisement.models import (PhotoAdvertisement, Advertisement, UploadFile, ErrorFile, Complaint,
                                  ReasonOfComplaint, AdvertisementAdmin, PhotoAdvertisementAdmin, UploadFileAdmin,
                                  ErrorFileAdmin, ComplaintAdmin, ReasonOfComplaintAdmin)

# Register your models here.
# admin.site.register(PhotoAdvertisement, PhotoAdvertisementAdmin)
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(UploadFile, UploadFileAdmin)
admin.site.register(ErrorFile, ErrorFileAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(ReasonOfComplaint, ReasonOfComplaintAdmin)
