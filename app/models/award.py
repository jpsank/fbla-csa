from sqlalchemy import func

from app import db
from .base import Base


class Award(Base):
    name = db.Column(db.String(1000), primary_key=True)
    about = db.Column(db.String(4000))

    def __repr__(self):
        return '<Award {}>'.format(self.name)

    @staticmethod
    def get_by_name(name):
        return Award.query.filter_by(name=name).first()

    def total_hours(self):
        total = 0
        for student in self.students:
            total += student.service_hours
        return total

