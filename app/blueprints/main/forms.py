from flask_wtf import FlaskForm
from wtforms import widgets, StringField, FloatField, IntegerField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

from app import db
from app.models import Student, Award
from app.util.validators import ValidName, Unique, ValidLength, NaturalNumber


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class StudentForm(FlaskForm):
    number = IntegerField('Student Number', validators=[NaturalNumber()])
    name = StringField('Name', validators=[DataRequired(), ValidLength(Student.name), ValidName()])
    grade = IntegerField('Grade')

    service_hours = FloatField('Service Hours')
    awards = MultiCheckboxField('Service Awards')

    submit = SubmitField('Submit')

    def __init__(self, student=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.awards.choices = [(award.name, award.name) for award in Award.query.all()]

        unique = Unique(Student.get_by_number)
        if student is not None:
            unique.allowed = [student.number]
        self.number.validators.append(unique)



class SearchForm(FlaskForm):
    search = StringField('Search')

