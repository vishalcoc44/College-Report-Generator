

College Event Report Generator

Overview
The College Event Report Generator is a Flask-based web application designed to streamline the process of creating comprehensive event reports for college events. It allows users to input event details, upload participant data, and automatically generates professional PDF reports with data visualizations.

Features
- User Authentication: Secure login and registration system with role-based access (staff/student)
- Event Management: Create and manage college events with detailed information
- Data Visualization: Automatic generation of charts and graphs based on participant data
- PDF Report Generation: Creates professional PDF reports with event details, statistics, and images
- File Upload: Support for uploading event posters, photos, and participant data (CSV format)
- Responsive UI: Modern, user-friendly interface with interactive elements

Project Structure

project/
├── app.py                 
├── config.py               
├── migrations/           
│   └── env.py              
├── static/                 
│   ├── choose.css         
│   ├── events.css          
│   └── index.css          
├── templates/              
│   ├── choose.html
│   ├── event_detail.html   
│   ├── events.html        
│   └── index.html        
└── README.md              

Technologies Used
- Backend: Flask, SQLAlchemy, Flask-Migrate
- Database: SQLite
- Data Processing: Pandas, Matplotlib, Seaborn
- PDF Generation: ReportLab
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask session management

Installation

Prerequisites
- Python 3.7+
- pip (Python package manager)

Setup
1. Clone the repository:
   
   git clone https://github.com/yourusername/college-event-report-generator.git
   cd college-event-report-generator


2. Create and activate a virtual environment:

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   
   pip install -r requirements.txt
   

4. Initialize the database:
   
   flask db init
   flask db migrate
   flask db upgrade
   

5. Run the application:
   
   python app.py


6. Access the application at `http://localhost:5000`

Usage

### User Registration and Login
1. Navigate to the home page
2. Register with a username, password, and teacher ID
3. Login with your credentials

### Creating an Event Report
1. After login, enter basic event details (name, date, faculty, etc.)
2. Upload an event poster image
3. Enter additional event details (address, timings, manager)
4. Upload participant data (CSV file)
5. Add achievements, testimonials, and feedback
6. Upload event photos
7. Submit to generate and download the PDF report

### CSV File Format
The application expects a CSV file with the following columns:
- name
- usn
- year
- branch
- section
- semester

## Configuration
The application configuration is stored in `config.py`. Key settings include:
- `SECRET_KEY`: For session security
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: Directory for uploaded files

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors
- Vishal S(https://github.com/vishalcoc44)
- Pihu MIttal
```

