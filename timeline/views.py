import collections
import dataclasses
import json
from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import render

from . import prepprocessor
from .models import TimelineImage, Person

image_folder = 'timeline/static/photos/images'


@dataclasses.dataclass
class Group:

    def __init__(self, total_weeks, age_string):
        self.total_weeks = total_weeks
        self.age_string = age_string
        self.c1 = []
        self.c2 = []


def show_images(request):
    persons = Person.objects.all()
    all_images = TimelineImage.objects.all()

    groups = defaultdict(list)

    image: TimelineImage
    for image in all_images:
        weeks = image.age_in_weeks()
        age_string = image.age()

        group = groups.get(weeks, Group(age_string=age_string, total_weeks=weeks))

        if image.person_name == persons[0]:
            group.c1.append(image)
        elif image.person_name == persons[1]:
            group.c2.append(image)
        else:
            print(f"unknown person {persons}")
            continue

        groups[weeks] = group

    groups = collections.OrderedDict(sorted(groups.items()))
    groups.default_factory = None

    context = {
        'persons': persons,
        'data': groups
    }

    return render(request, 'timeline/image_gallery.html', context)


def autoimport(request):
    result = prepprocessor.import_images("input", image_folder)
    return HttpResponse(json.dumps(result))
