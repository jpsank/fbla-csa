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
