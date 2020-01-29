from flask import current_app
import json, random
import os

from app import db
from app.models import Student, Award
from config import basedir


def create_award(a):
    return Award(name=a["name"], about=a["about"])


with open(os.path.join(basedir, "app/populate/awards.json"), "r") as f:
    awards = json.load(f)
for award in awards:
    db.session.add(create_award(award))
db.session.commit()


def student_factory(n=50):
    with open(os.path.join(basedir, "app/populate/firstnames.json"), "r") as f:
        first_names = json.load(f)
    with open(os.path.join(basedir, "app/populate/surnames.json"), "r") as f:
        last_names = json.load(f)

    possible_awards = [("Community", 50), ("Service", 200), ("Achievement", 500)]
    possible_awards = [(Award.get_by_name(name), h) for (name, h) in possible_awards]

    for i in range(n):
        first = random.choice(first_names)
        last = random.choice(last_names)
        hours = round(random.random()*800)

        stud = Student(number=i, name=first + " " + last,
                       grade=random.randint(9, 12), service_hours=hours)
        for (a, min_hours) in possible_awards:
            if hours >= min_hours:
                stud.give_award(a)

        yield stud


for student in student_factory():
    db.session.add(student)
db.session.commit()
