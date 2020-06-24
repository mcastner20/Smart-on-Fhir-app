from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
#patients Name: Jason Argonaut dob: 08 01 1985
global questions_list
questions_range = list(range(34, 94))
questions_range2 = list(range(234, 294))
questions_list = ['question 1 [Redacted]', 'question 2 [Redacted]']

app = Flask(__name__)
app.config['SQLALCHEMY_DABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

def APIsearch(first_name, last_name, dob, conditions, medications, immunizations, allergies, condition_codes, medication_codes, immunization_codes, allergy_codes):
    year = dob[:4]
    day = dob[5:7]
    month = dob[8:]
    dob = year+'-'+month+'-'+day
    url = "https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Patient?family="+last_name+'&given='+first_name+'&birthdate='+dob
    document = requests.get(url)
    soup = BeautifulSoup(document.content, 'xml')
    id = soup.id['value']
    url = "https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Condition?patient="+id
    document = requests.get(url)
    soup = BeautifulSoup(document.content, 'xml')
    for code in soup.find_all('code'):
        for text in code.find_all('text'):
            conditions.append(text['value'])
    url = "https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/MedicationOrder?patient=" + id
    document = requests.get(url)
    soup = BeautifulSoup(document.content, 'xml')
    for medication in soup.find_all('medicationReference'):
        for display in medication.find_all('display'):
            medications.append(display['value'].title())
    url = "https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/Immunization?patient=" + id
    document = requests.get(url)
    soup = BeautifulSoup(document.content, 'xml')
    for code in soup.find_all('vaccineCode'):
        for text in code.find_all('text'):
            immunizations.append(text['value'])
    url = "https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/AllergyIntolerance?patient=" + id
    document = requests.get(url)
    soup = BeautifulSoup(document.content, 'xml')
    for substance in soup.find_all('substance'):
        for text in substance.find_all('text'):
            allergies.append(text['value'].title())
    for substance in soup.find_all('substance'):
        code = substance.find('code')
        allergy_codes.append(code['value'])

    return id, dob

class data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(100), nullable=False)


    def __init__(self, first_name, last_name, dob):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob



    def __repr__(self):
        return 'DATA ' + str(self.id)


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('home.html')

@app.route('/questions', methods=['GET', 'POST'])

def questions():
    if request.method == 'POST':

        first = request.form['first_name']
        last = request.form['last_name']
        do = request.form['dob']
        global first_name
        global last_name
        date = do
        first_name = first
        last_name = last
        global id
        global dob
        global conditions
        global medications
        global immunizations
        global allergies
        global condition_codes
        global medication_codes
        global immunization_codes
        global allergy_codes
        conditions = []
        medications = []
        immunizations = []
        allergies = []
        condition_codes, medication_codes, immunization_codes, allergy_codes = [], [], [], []
        id, dob = APIsearch(first_name, last_name, date, conditions, medications, immunizations, allergies, condition_codes, medication_codes, immunization_codes, allergy_codes)

        new_data = data(first_name=first_name, last_name=last_name, dob=dob)

        try:
            db.session.add(new_data)
            db.session.commit()

            return redirect('/questions')
        except:
            return "There was an error"
    else:
        tasks = data.query.all()
        return render_template('questions.html', tasks = tasks, dob=dob, id = id, conditions=conditions, first_name=first_name, last_name=last_name, medications=medications, immunizations=immunizations, allergies=allergies)
        """first_name=first_name, last_name=last_name"""

@app.route('/disaster', methods=['GET', 'POST'])
def disaster():
    return render_template('disaster.html')

@app.route('/demographic', methods=['GET', 'POST'])
def demographic():
    return render_template('demographic.html')
@app.route('/hazard', methods=['GET', 'POST'])
def hazard():
    return render_template('hazard2.html', range=questions_range, questions_list=questions_list)
@app.route('/hazard_continued', methods=['GET', 'POST'])
def hazard_continued():
    if request.method == 'POST':
        global answers
        answers = []
        for item in questions_range:
            try:
                q = request.form[str(item)]
                answers.append(q)
            except KeyError:
                answers.append('No')
        global new_questions_list
        new_questions_list = []
        for answer, question in zip(answers, questions_list):
            if answer == 'Yes':
                new_questions_list.append(question)
        global new_range
        new_range = len(new_questions_list)
        new_range = list(range(100, 100+int(new_range)))
        return redirect('/hazard_continued')

    else:
        return render_template('disaster_continued.html', questions=new_questions_list, new_range=new_range)

@app.route('/hazard_probability', methods=['GET', 'POST'])
def hazard_probability():
    return render_template('hazard_probability.html', range=questions_range2, questions_list=questions_list)
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

