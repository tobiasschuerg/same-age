import collections
import dataclasses
from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import render

from . import prepprocessor
from .models import TimelineImage, Person

image_folder = 'timeline/static/photos/images'


@dataclasses.dataclass
class Group:

    def __init__(self, age):
        self.age = age
        self.c1 = []
        self.c2 = []


def show_images(request):
    persons = Person.objects.all()
    all_images = TimelineImage.objects.all()

    groups = defaultdict(list)

    image: TimelineImage
    for image in all_images:
        age = image.age()

        group = groups.get(age, Group(age=age))

        if image.person_name == persons[0]:
            group.c1.append(image.file_name)
        elif image.person_name == persons[1]:
            group.c2.append(image.file_name)
        else:
            print(f"unknown person {persons}")
            continue

        groups[age] = group

    groups = collections.OrderedDict(sorted(groups.items()))
    groups.default_factory = None

    context = {
        'persons': persons,
        'data': groups
    }

    return render(request, 'timeline/image_gallery.html', context)


def autoimport(request):
    result = prepprocessor.import_images("input", image_folder)
    return HttpResponse(str(result))
