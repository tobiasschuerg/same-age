import collections
import dataclasses
import json
from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import render

from . import importer
from .models import TimelineImage, Person

image_folder = 'timeline/static/photos/images'


@dataclasses.dataclass
class Group:

    def __init__(self, total_weeks, age_string, num_persons):
        self.total_weeks = total_weeks
        self.age_string = age_string
        self.columns = [[] for _ in range(num_persons)]


def show_images(request):
    persons = list(Person.objects.all())
    all_images = TimelineImage.objects.all()

    person_index = {person.id: i for i, person in enumerate(persons)}
    num_persons = len(persons)

    groups = defaultdict(list)

    image: TimelineImage
    for image in all_images:
        weeks = image.age_in_weeks()
        age_string = image.age()

        group = groups.get(weeks, Group(age_string=age_string, total_weeks=weeks, num_persons=num_persons))
        group.columns[person_index[image.person_id]].append(image)

        groups[weeks] = group

    groups = collections.OrderedDict(sorted(groups.items()))
    groups.default_factory = None

    context = {
        'persons': persons,
        'data': groups
    }

    return render(request, 'timeline/image_gallery.html', context)


def autoimport(request):
    result = importer.import_images("input", image_folder)
    return HttpResponse(json.dumps(result))
