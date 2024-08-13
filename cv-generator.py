from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = ''  # Reemplaza con una clave secreta real en producción
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class CVForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    title = StringField('Título', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    phone = StringField('Teléfono', validators=[Optional()])
    linkedin = StringField('URL de LinkedIn', validators=[Optional()])
    summary = TextAreaField('Resumen Profesional', validators=[Optional()])
    experience = TextAreaField('Experiencia Laboral', validators=[Optional()])
    education = TextAreaField('Educación', validators=[Optional()])
    skills = TextAreaField('Habilidades', validators=[Optional()])
    projects = TextAreaField('Proyectos Destacados', validators=[Optional()])
    photo = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Solo imágenes!'), Optional()])
    submit = SubmitField('Generar CV')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CVForm()
    if form.validate_on_submit():
        photo_filename = None
        if form.photo.data:
            photo = form.photo.data
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        cv_data = {k: v for k, v in form.data.items() if v and k != 'csrf_token' and k != 'submit'}
        if photo_filename:
            cv_data['photo'] = photo_filename
        
        # Convertir habilidades en una lista, separando por saltos de línea
        if 'skills' in cv_data:
            cv_data['skills'] = ','.join([skill.strip() for skill in cv_data['skills'].split('\n') if skill.strip()])
        
        return redirect(url_for('cv', **cv_data))
    return render_template('form.html', form=form)

@app.route('/cv')
def cv():
    cv_data = {k: v for k, v in request.args.items() if v}
    if 'skills' in cv_data:
        cv_data['skills'] = cv_data['skills'].split(',')
    return render_template('cv_iframe.html', **cv_data)

@app.route('/cv-content')
def cv_content():
    cv_data = {k: v for k, v in request.args.items() if v}
    if 'skills' in cv_data:
        cv_data['skills'] = cv_data['skills'].split(',')
    return render_template('cv.html', **cv_data)

@app.route('/download-cv')
def download_cv():
    cv_data = {k: v for k, v in request.args.items() if v}
    if 'skills' in cv_data:
        cv_data['skills'] = cv_data['skills'].split(',')
    rendered = render_template('cv.html', **cv_data)
    response = make_response(rendered)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename=cv.html'
    return response

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)