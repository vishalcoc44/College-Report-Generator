import os
from flask import Flask, request, render_template, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
import logging
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = r'C:\Users\Vishal\OneDrive\Desktop\Special Topics Project'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    timings = db.Column(db.String(50), nullable=False)
    manager = db.Column(db.String(50), nullable=False)
    achievements = db.Column(db.String(200))
    testimonials = db.Column(db.String(200))
    feedback = db.Column(db.String(200))
    expenses = db.Column(db.Float)
    photos = db.Column(db.String(200))
    google_form_file = db.Column(db.String(200), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)

def init_teacher_ids():
    with app.app_context():
        teacher_ids = ['1234', '5678', '9012']
        for teacher_id in teacher_ids:
            existing_teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
            if existing_teacher:
                print(f"Teacher ID {teacher_id} already exists in the database.")
            else:
                print(f"Inserting Teacher ID {teacher_id} into the database.")
                teacher = Teacher(teacher_id=teacher_id)
                db.session.add(teacher)
        try:
            db.session.commit()
        except Exception as e:
            print(f"An error occurred while committing to the database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_teacher_ids()
    
with app.app_context():
    db.create_all()
    init_teacher_ids()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report')
def generate_report_route():
    return generate_report()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['logged_in'] = True
        return redirect(url_for('choose'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('index'))

@app.route('/choose')
def choose():
    return render_template('choose.html')

@app.route('/submit_event', methods=['POST'])
def submit_event():
    event_name = request.form['eventName']
    event_date = request.form['eventDate']
    faculty_names = request.form['facultyNames']
    student_coordinators = request.form['studentCoordinators']
    speaker_name = request.form['speakerName']
    about_speaker = request.form['aboutSpeaker']
    poster_image = request.files['posterImage']

    if poster_image:
        poster_filename = secure_filename(poster_image.filename)
        poster_path = os.path.join(app.config['UPLOAD_FOLDER'], poster_filename)
        poster_image.save(poster_path)
        session['poster_image'] = poster_path
    else:
        flash('Poster image upload failed. Please try again.', 'error')
        return redirect(url_for('choose'))

    session['event_name'] = event_name
    session['event_date'] = event_date
    session['faculty_names'] = faculty_names
    session['student_coordinators'] = student_coordinators
    session['speaker_name'] = speaker_name
    session['about_speaker'] = about_speaker
    
    return redirect(url_for('events'))

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/register', methods=['POST'])
def register():
    pass

@app.route('/submit_event_details', methods=['POST'])
def submit_event_details():
    event_address = request.form['eventAddress']
    event_timings = request.form['eventTimings']
    event_manager = request.form['eventManager']
    expenses = request.form['expenses']
    achievements = request.form['achievements']
    testimonials = request.form['testimonials']
    feedback = request.form['feedback']
    google_form_file = request.files['googleFormFile']
    
    photos = request.files.getlist('photos')
    photo_paths = []
    for photo in photos:
        photo_filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        photo.save(photo_path)
        photo_paths.append(photo_path)

    if google_form_file:
        filename = secure_filename(google_form_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        google_form_file.save(file_path)
        session['google_form_file'] = file_path
    else:
        flash('File upload failed. Please try again.', 'error')
        return redirect(url_for('events'))
    
    background_image = request.files.get('backgroundImage')
    if background_image:
        background_filename = secure_filename(background_image.filename)
        background_path = os.path.join(app.config['UPLOAD_FOLDER'], background_filename)
        background_image.save(background_path)
        session['background_image'] = background_path
    else:
        session['background_image'] = None
    
    session['event_address'] = event_address
    session['event_timings'] = event_timings
    session['event_manager'] = event_manager
    session['expenses'] = expenses
    session['achievements'] = achievements
    session['testimonials'] = testimonials
    session['feedback'] = feedback
    session['photos'] = ','.join(photo_paths)
    
    event = Event(
        name=session['event_name'],
        date=session['event_date'],
        address=event_address,
        timings=event_timings,
        manager=event_manager,
        expenses=0.0,
        achievements=achievements,
        testimonials=testimonials,
        feedback=feedback,
        photos=session['photos'],
        google_form_file=file_path,
            )
    db.session.add(event)
    db.session.commit()
    
    try:
        pdf_path = generate_report()
        flash('Report generated successfully!', 'success')
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating report: {e}")
        flash(f'Error generating report: {e}', 'error')
        return redirect(url_for('events'))
    
def generate_report():
    try:
        event_name = session.get('event_name')
        event_date = session.get('event_date')
        student_coordinators = session.get('student_coordinators')
        faculty_names = session.get('faculty_names')
        speaker_name = session.get('speaker_name')
        about_speaker = session.get('about_speaker')
        poster_image = session.get('poster_image')
        event_address = session.get('event_address')
        event_timings = session.get('event_timings')
        event_manager = session.get('event_manager')
        google_form_file = session.get('google_form_file')
        expenses = session.get('expenses')
        achievements = session.get('achievements')
        testimonials = session.get('testimonials')
        feedback = session.get('feedback')
        photos = session.get('photos', '').split(',')
        background_image = session.get('background_image')

        if not all([event_name, event_date, student_coordinators, faculty_names, speaker_name, about_speaker, poster_image, event_address, event_timings, event_manager, google_form_file]):
            raise ValueError("Some required session data is missing.")

        try:
            data = pd.read_csv(google_form_file, encoding='utf-8', sep=',')
        except UnicodeDecodeError:
            data = pd.read_csv(google_form_file, encoding='latin1', sep=',')

        required_columns = ['name', 'usn', 'year', 'branch', 'section', 'semester']
        for col in required_columns:
            if col.lower() not in data.columns.str.lower():
                raise ValueError(f"CSV file does not contain the required '{col}' column.")

        registrations = len(data)
        registration_page_visits = 141
        registration_conversion_rate = max((registrations / registration_page_visits) * 100, 0)
        auditorium_visitors = 74
        data_analysis_generated_plots = 5

        registration_counts = data['year'].value_counts()
        branch_counts = data['branch'].value_counts()
        section_counts = data['section'].value_counts()
        semester_counts = data['semester'].value_counts()

        fig, axes = plt.subplots(2, 2, figsize=(14, 14))

        sns.barplot(x=registration_counts.index, y=registration_counts.values, ax=axes[0, 0]).set_title('Registrations by Year')
        sns.barplot(x=branch_counts.index, y=branch_counts.values, ax=axes[0, 1]).set_title('Registrations by Branch')
        sns.barplot(x=section_counts.index, y=section_counts.values, ax=axes[1, 0]).set_title('Registrations by Sections')
        sns.barplot(x=semester_counts.index, y=semester_counts.values, ax=axes[1, 1]).set_title('Registrations by Semester')

        plt.tight_layout()
        plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data_analysis_plots.png')
        plt.savefig(plot_path)
        plt.close()

        heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], 'heatmap.png')
        scatter_plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'scatter_plot.png')

        # Create Heatmap
        numeric_data = data.select_dtypes(include='number')
        heatmap_data = numeric_data.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(heatmap_path)
        plt.close()

        # Create Scatter Plot
        plt.figure(figsize=(10, 8))
        sns.scatterplot(data=data, x='year', y='semester', hue='branch')
        plt.title('Scatter Plot')
        plt.tight_layout()
        plt.savefig(scatter_plot_path)
        plt.close()

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'event_report.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        title_style = ParagraphStyle(
            'title_style',
            fontSize=18,
            leading=22,
            alignment=1,
            textColor=HexColor('#2E7D32')
        )
        header_style = ParagraphStyle(
            'header_style',
            fontSize=14,
            leading=18,
            textColor=HexColor('#2E7D32')
        )
        body_style = ParagraphStyle(
            'body_style',
            fontSize=12,
            leading=14.5,
            textColor=HexColor('#000000')
        )

        elements.append(Paragraph("Event Report", title_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Event Details", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Event Name: {event_name}", body_style))
        elements.append(Paragraph(f"Event Date: {event_date}", body_style))
        elements.append(Paragraph(f"Event Address: {event_address}", body_style))
        elements.append(Paragraph(f"Event Timings: {event_timings}", body_style))
        elements.append(Paragraph(f"Event Manager: {event_manager}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Participants", header_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Number of Participants: {registrations}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Coordinator Details", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Faculty Names: {faculty_names}", body_style))
        elements.append(Paragraph(f"Student Coordinators: {student_coordinators}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Guest Details", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Guest Name: {speaker_name}", body_style))
        elements.append(Paragraph(f"About Guest: {about_speaker}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Analysis and Outcomes", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Registration Page Visits: {registration_page_visits}", body_style))
        elements.append(Paragraph(f"Registrations: {registrations}", body_style))
        elements.append(Paragraph(f"Auditorium Visitors: {auditorium_visitors}", body_style))
        elements.append(Paragraph(f"Registration Conversion Rate: {registration_conversion_rate:.2f}%", body_style))
        elements.append(Paragraph(f"Data Analysis Generated Plots: {data_analysis_generated_plots}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Achievements", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(achievements, body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Testimonials", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(testimonials, body_style))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Feedback", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(feedback, body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Expenses", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Total Expenses: {expenses}", body_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Event Poster", header_style))
        elements.append(Spacer(1, 12))

        elements.append(Image(poster_image, width=6 * inch, height=4 * inch))
        elements.append(PageBreak())

        elements.append(Paragraph("Event Photos", header_style))
        elements.append(Spacer(1, 12))

        for photo in photos:
            elements.append(Image(photo, width=6 * inch, height=4 * inch))
            elements.append(Spacer(1, 12))

        elements.append(PageBreak())

        elements.append(Paragraph("Registration Data Analysis", header_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(plot_path, width=6 * inch, height=4 * inch))
        elements.append(Spacer(1, 12))

        elements.append(PageBreak())

        elements.append(Paragraph("Correlation Heatmap", header_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(heatmap_path, width=6 * inch, height=4 * inch))
        elements.append(Spacer(1, 12))

        elements.append(PageBreak())

        elements.append(Paragraph("Scatter Plot", header_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(scatter_plot_path, width=6 * inch, height=4 * inch))
        elements.append(Spacer(1, 12))

        if background_image:
            background_img = Image(background_image, width=letter[0], height=letter[1])
           
            for element in elements:
                element.wrapOn(background_img, letter[0], letter[1])
                element.drawOn(background_img, 0, 0)
            elements.insert(0, background_img)

        doc.build(elements)

        return pdf_path

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        raise


if __name__ == '__main__':
    app.run(debug=True)
       

