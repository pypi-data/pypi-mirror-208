from pathlib import Path, PurePath
from django import template
from django.db.models.fields.files import ImageFieldFile

register = template.Library()

@register.filter(is_safe=True)
def getOptimizedImage(img, rez:str, ext:str):
    imagePath = Path(img.url)
    fileName = imagePath.stem
    parent = imagePath.parent
    return str(PurePath(parent,fileName+rez+ext))

@register.filter(is_safe=True)
def srcSet(image:ImageFieldFile):
    if (image):
        returnString = f"""
            src="{getOptimizedImage(image, "_sm", ".webp")}" 
            srcset="{getOptimizedImage(image, "_lg", ".webp")} 1024w, 
                    {getOptimizedImage(image, "_md", ".webp")} 640w, 
                    {getOptimizedImage(image, "_sm", ".webp") } 360w" 
            loading="lazy" 
            sizes="100vw" """
    else:
        returnString = ""
    return returnString