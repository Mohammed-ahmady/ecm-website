from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates the Site domain to match settings.SITE_DOMAIN'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            old_domain = site.domain
            if old_domain != settings.SITE_DOMAIN:
                site.domain = settings.SITE_DOMAIN
                site.name = 'Magirus Center'
                site.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully updated site domain from "{old_domain}" to "{settings.SITE_DOMAIN}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Site domain already set to {site.domain}'))
        except Site.DoesNotExist:
            Site.objects.create(
                id=settings.SITE_ID,
                domain=settings.SITE_DOMAIN,
                name='Magirus Center'
            )
            self.stdout.write(self.style.SUCCESS(f'Created new site with domain {settings.SITE_DOMAIN}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating site domain: {e}'))
