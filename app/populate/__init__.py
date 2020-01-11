from flask import current_app
import json
import os

from app import db
from app.models import Student, Award
from config import basedir


def create_student(stud):
    s = Student(number=stud["number"], name=stud["name"], grade=stud["grade"], service_hours=stud["service_hours"])
    if "awards" in stud:
        for award_name in stud["awards"]:
            s.give_award(Award.get_by_name(award_name))
    return s


def create_award(a):
    return Award(name=a["name"], about=a["about"])


with open(os.path.join(basedir, "app/populate/awards.json"), "r") as f:
    awards = json.load(f)
for award in awards:
    db.session.add(create_award(award))
db.session.commit()


with open(os.path.join(basedir, "app/populate/fake_students.json"), "r") as f:
    fake_students = json.load(f)
for student in fake_students:
    db.session.add(create_student(student))
db.session.commit()
