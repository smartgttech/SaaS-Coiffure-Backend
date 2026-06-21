from django.db import models
from tenants.models import Tenant


class JournalAction(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='journal_actions'
    )
    utilisateur_id = models.IntegerField(null=True, blank=True)
    utilisateur_email = models.EmailField(null=True, blank=True)
    type_action = models.CharField(max_length=100)
    ressource = models.CharField(max_length=100)
    ressource_id = models.IntegerField(null=True, blank=True)
    details_avant = models.JSONField(null=True, blank=True)
    details_apres = models.JSONField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Action journalisée"
        verbose_name_plural = "Journal des actions"
        ordering = ['-date']

    def __str__(self):
        return f"{self.type_action} — {self.utilisateur_email} — {self.date}"