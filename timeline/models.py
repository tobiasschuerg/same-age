from datetime import date

from django.db import models

from timeline.utils import diff_str, get_number_of_weeks


class Person(models.Model):
    name = models.CharField(max_length=200)
    birthday = models.DateField()

    def __str__(self):
        return self.name


class TimelineImage(models.Model):
    file_name = models.CharField(max_length=255)
    original_file_name = models.CharField(max_length=255)
    capture_date = models.DateTimeField()
    record_date = models.DateTimeField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_name_id')

    def __str__(self):
        return self.file_name

    def age_in_weeks(self):
        return get_number_of_weeks(self.person.birthday, self.capture_date.date())

    @staticmethod
    def age_in_months(birthday: date, other_date: date) -> int:
        age_in_months = (other_date.year - birthday.year) * 12 + (other_date.month - birthday.month)
        if other_date.day < birthday.day:
            age_in_months -= 1
        return age_in_months

    def age(self):
        return diff_str(self.person.birthday, self.capture_date.date())
