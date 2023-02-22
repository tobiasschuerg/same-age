import os
import uuid
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

from .models import TimelineImage, Person


def fix_image_rotation(img):
    exif_data = img.getexif()
    orientation = 1  # default to no rotation if no exif data is present
    # Find the orientation tag
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == 'Orientation':
            orientation = value
            break

    # Rotate the image according to the orientation tag
    if orientation == 3:
        img = img.rotate(180)
    elif orientation == 6:
        img = img.rotate(-90)
    elif orientation == 8:
        img = img.rotate(90)

    return img


def import_images(input_folder, output_folder):
    for name in os.listdir(input_folder):
        person = Person.objects.filter(name=name)
        if not person:
            person = Person(name=name, birthday=datetime.now())
            person.save()
        else:
            person = person[0]
        process_images(input_folder, person, output_folder)


def process_images(input_root, person, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    input_dir = os.path.join(input_root, person.name)
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue  # skip non-image files
        input_path = os.path.join(input_dir, filename)
        output_filename = person.name + '_' + str(uuid.uuid4()) + '.jpg'
        output_path = os.path.join(output_dir, output_filename)
        capture_date = None
        with Image.open(input_path) as img:
            exif_data = img._getexif()
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    capture_date_str = str(value)
                    capture_date = datetime.strptime(capture_date_str, '%Y:%m:%d %H:%M:%S')
            # fix orientation
            img = fix_image_rotation(img)
            # resize to 800 pixels
            img.thumbnail((800, 800))
            # save to output directory with uuid as filename
            img.save(output_path)
            # get creation date from EXIF data

        record_creation_date = datetime.now()

        found = TimelineImage.objects.filter(original_file_name=filename, capture_date=capture_date)
        if found:
            print(f"Skipping {filename} as it already exists")
        else:
            # create database entry
            TimelineImage(
                file_name=output_filename,
                original_file_name=filename,
                capture_date=capture_date,
                record_date=record_creation_date,
                person_name=person
            ).save()
