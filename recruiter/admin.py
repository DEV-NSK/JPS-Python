from django.contrib import admin
from .models import RecruiterPin, ShortlistAudit, CandidateTimeline, BlindHiringReveal, TalentPool

admin.site.register(RecruiterPin)
admin.site.register(ShortlistAudit)
admin.site.register(CandidateTimeline)
admin.site.register(BlindHiringReveal)
admin.site.register(TalentPool)
