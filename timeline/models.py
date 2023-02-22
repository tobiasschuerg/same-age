from datetime import date

from django.db import models


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
    person_name = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.file_name

    @staticmethod
    def age_in_days(birthday, other_date):
        return (other_date - birthday).days

    @staticmethod
    def age_in_weeks(birthday, other_date):
        age_in_days = (other_date - birthday).days
        age_in_weeks = age_in_days // 7
        return age_in_weeks

    @staticmethod
    def age_in_months(birthday: date, other_date: date) -> int:
        age_in_months = (other_date.year - birthday.year) * 12 + (other_date.month - birthday.month)
        if other_date.day < birthday.day:
            age_in_months -= 1
        return age_in_months

    def age(self):
        return self.age_in_weeks(self.person_name.birthday, self.capture_date.date())
