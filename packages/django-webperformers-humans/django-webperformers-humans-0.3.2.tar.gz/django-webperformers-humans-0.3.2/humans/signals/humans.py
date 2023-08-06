from django.db.models.signals import post_save
from django.dispatch import receiver
from humans.helpers.images import resizeImage
from humans.models import Human

import logging
logger = logging.getLogger('django')

@receiver(post_save, sender=Human)
def HumanPostSaveHandler(sender, instance:Human, **kwargs):
    try:
        resizeImage (instance.image.path)
    except Exception as ex:  # to handle initial object creation
        logger.error(f"Signal error on portfolio post {str(instance.pk)}:{ex.__str__()}")
        return None  # just exiting from signal