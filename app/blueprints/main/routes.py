from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, make_response, session
from flask_login import current_user, login_required
from sqlalchemy import func
import pdfkit
from functools import wraps

from app.blueprints.main import bp
from app import db
from app.models import Student, Award
from app.blueprints.main.forms import StudentForm, SearchForm, AdminPassForm


def paginate(items, per_page=None):
    if per_page is None:
        per_page = current_app.config['DEFAULT_PER_PAGE']

    page = request.args.get('page', 1, type=int)
    items = items.paginate(page, per_page, False)

    next_url = url_for(request.endpoint, page=items.next_num) if items.has_next else None
    prev_url = url_for(request.endpoint, page=items.prev_num) if items.has_prev else None
    return items, next_url, prev_url


def admin_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not is_admin():
            flash('You must log in to access this page.')
            return redirect(url_for('main.login'))
        return fn(*args, **kwargs)
    return decorated_view


def is_admin():
    return 'is_admin' in session


def login_admin():
    session['is_admin'] = ''


def logout_admin():
    session.pop('is_admin')


def render_admin_template(*args, **kwargs):
    return render_template(*args, **kwargs, is_admin=is_admin())


# ------------------------------ LOGIN ------------------------------


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(url_for('main.index'))
    form = AdminPassForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config['ADMIN_PASS']:
            login_admin()
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
            return redirect(url_for('main.login'))
    return render_admin_template('main/login.html', title='Admin Login', form=form)


@bp.route('/logout')
@admin_required
def logout():
    logout_admin()
    return redirect(url_for('main.index'))


# ------------------------------ FRONT PAGES ------------------------------

@bp.route('/')
@bp.route('/index')
def index():
    return render_admin_template('main/home.html', title='Home')


@bp.route('/students', methods=['GET', 'POST'])
def students_page():
    search_form = SearchForm()
    students = Student.query

    if search_form.validate_on_submit():
        students = students.filter(Student.name.like('%' + search_form.search.data + '%') |
                                   Student.number.like('%' + search_form.search.data + '%'))

    students, next_url, prev_url = paginate(students)

    return render_admin_template('main/students.html', title='Students',
                                 search_form=search_form,
                                 students=students.items, next_url=next_url, prev_url=prev_url)


@bp.route('/awards', methods=['GET'])
def award_categories():
    awards = Award.query.all()
    return render_admin_template('main/award_categories.html', title='Types of Awards', awards=awards)


@bp.route('/award/<award_name>', methods=['GET', 'POST'])
def award_page(award_name):
    award = Award.get_by_name(award_name)
    if award is None:
        return abort(404)

    search_form = SearchForm()
    students = Student.query.filter(Student.awards.any(Award.name == award.name))

    if search_form.validate_on_submit():
        students = students.filter(Student.name.like('%' + search_form.search.data + '%') |
                                   Student.number.like('%' + search_form.search.data + '%'))

    students, next_url, prev_url = paginate(students)

    return render_admin_template('main/award_page.html', title='{} Award'.format(award.name),
                                 search_form=search_form,
                                 award=award, students=students.items, next_url=next_url, prev_url=prev_url)


# ------------------------------ STUDENTS ------------------------------

@bp.route('/student/<number>')
def show_student(number):
    student = Student.get_by_number(number)
    if student is None:
        return abort(404)
    return render_admin_template('main/student.html', student=student)


@bp.route('/edit_student/<number>', methods=['GET', 'POST'])
@admin_required
def edit_student(number):
    student = Student.get_by_number(number)
    if student is None:
        return abort(404)

    form = StudentForm(student)
    if form.validate_on_submit():
        student.number = form.number.data
        student.name = form.name.data
        student.grade = form.grade.data
        student.service_hours = form.service_hours.data

        student.clear_awards()
        for award_name in form.awards.data:
            student.give_award(Award.get_by_name(award_name))

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.show_student', number=student.number))
    elif request.method == 'GET':
        form.name.default = student.name
        form.number.default = student.number
        form.grade.default = student.grade
        form.service_hours.default = student.service_hours
        form.awards.default = [award.name for award in student.awards]

        form.process()

    return render_admin_template('main/edit_student.html', student=student, title='Edit Student',
                                 form=form)


@bp.route('/create_student', methods=['GET', 'POST'])
@admin_required
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(number=form.number.data, name=form.name.data, grade=form.grade.data,
                          service_hours=form.service_hours.data)

        for award_name in form.awards.data:
            student.give_award(Award.get_by_name(award_name))

        db.session.add(student)
        db.session.commit()
        flash('Your new student has been saved.')
        return redirect(url_for('main.show_student', number=student.number))

    return render_admin_template('main/create_student.html', title='New Student',
                                 form=form)


@bp.route('/delete_student/<number>')
@admin_required
def delete_student(number):
    student = Student.get_by_number(number)
    if student is None:
        flash('The student you are trying to delete does not exist.')
        return redirect(url_for('main.students_page'))

    db.session.delete(student)
    db.session.commit()
    flash('You deleted the student.')
    return redirect(url_for('main.students_page'))


# ------------------------------ REPORTS ------------------------------

def render_template_as_pdf(template_name, **context):
    rendered = render_template(template_name, **context)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = "inline; filename=output.pdf"
    return response


@bp.route('/per_student_report', methods=['GET'])
@admin_required
def per_student_report():
    students = Student.query.all()
    return render_template_as_pdf('reports/per_student_report.html', students=students)


@bp.route('/per_award_report', methods=['GET'])
@admin_required
def per_award_report():
    awards = Award.query.all()
    return render_template_as_pdf('reports/per_award_report.html', awards=awards)
