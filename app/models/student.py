from sqlalchemy import func

from app import db
from .base import Base


awards_given = db.Table(
    'awards_given',
    db.Column('student_number', db.Integer, db.ForeignKey('student.number')),
    db.Column('award_name', db.Integer, db.ForeignKey('award.name'))
)


class Student(Base):
    number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    grade = db.Column(db.Integer)

    service_hours = db.Column(db.Float)

    # Community Service Awards
    awards = db.relationship(
        'Award', secondary='awards_given',
        backref=db.backref('students', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Student {}>'.format(self.name)

    # Awards

    def clear_awards(self):
        self.awards = []

    def give_award(self, award):
        if not self.has_award(award):
            self.awards.append(award)

    def has_award(self, award):
        return award in self.awards

    # Query methods

    @staticmethod
    def get_by_name(name):
        return Student.query.filter(func.lower(Student.name) == func.lower(name)).first()

    @staticmethod
    def get_by_number(number):
        return Student.query.filter_by(number=number).first()

    @staticmethod
    def query_by_awards(c=None, s=None, a=None):
        query = Student.query
        if c is not None:
            query = query.filter_by(community=c)
        if s is not None:
            query = query.filter_by(service=s)
        if a is not None:
            query = query.filter_by(achievement=a)
        return query

    # Render

    def joined_awards(self):
        return ", ".join(award.name for award in self.awards)
