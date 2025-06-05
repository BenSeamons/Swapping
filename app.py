from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flashing messages

students = []
def parse_google_form_spreadsheet(df):
    students_expanded = []
    rounds = 9  # Number of rounds

    for _, row in df.iterrows():
        name = str(row.get('Name', '')).strip()
        phone = str(row.get('Phone Number', '')).strip()
        email = str(row.get('Email Address', '')).strip()
        selective_specialty = str(row.get('Selective Specialty', '')).strip()
        selective_location = str(row.get('Selective Location', '')).strip()

        default_trade_status = 'open'  # Change if you want another default

        for i in range(1, rounds + 1):
            spec_col = f'Round {i} Specialty'
            loc_col = f'Round {i} Location'
            specialty = str(row.get(spec_col, '')).strip()
            location = str(row.get(loc_col, '')).strip()
            if specialty and location:
                students_expanded.append({
                    'name': name,
                    'phone': phone or email,
                    'email': email,
                    'specialty': specialty,
                    'block': f'Round {i}',
                    'location': location,
                    'trade_status': default_trade_status
                })

        # Add selective round if present
        if selective_specialty and selective_location:
            students_expanded.append({
                'name': name,
                'phone': phone or email,
                'email': email,
                'specialty': selective_specialty,
                'block': 'Selective',
                'location': selective_location,
                'trade_status': default_trade_status
            })

    return students_expanded

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('No file selected', 'error')
            return redirect(request.url)

        try:
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                flash('Unsupported file type. Upload .xlsx or .csv only.', 'error')
                return redirect(request.url)

            # Parse and expand Google Form spreadsheet
            new_students = parse_google_form_spreadsheet(df)

            count = 0
            for new_s in new_students:
                existing = next((s for s in students if
                                s['name'].lower() == new_s['name'].lower() and
                                s['specialty'].lower() == new_s['specialty'].lower() and
                                s['block'].lower() == new_s['block'].lower()), None)
                if existing:
                    existing.update(new_s)
                else:
                    students.append(new_s)
                count += 1

            flash(f'Successfully imported {count} clerkship records!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            flash(f'Error processing file: {e}', 'error')
            return redirect(request.url)

    return render_template('upload.html')

def categorize_candidate(candidate_status):
    if candidate_status == 'willing':
        return "🔥 Highest priority — willing to trade"
    elif candidate_status == 'wanting':
        return "⚡ High priority — wants to trade"
    elif candidate_status == 'open':
        return "✨ Medium priority — open to contact"
    else:
        return "❄️ Low priority — not trading"

def find_matches(students):
    matches = []
    filtered = [s for s in students if s['trade_status'] != 'no_trade']

    index = {}
    for s in filtered:
        key = (s['specialty'].lower(), s['block'].lower())
        index.setdefault(key, []).append(s)

    for key, group in index.items():
        willing = [s for s in group if s['trade_status'] == 'willing']
        wanting_or_open = [s for s in group if s['trade_status'] in ('wanting', 'open')]

        for w in willing:
            for wo in wanting_or_open:
                if w['name'] != wo['name']:
                    matches.append({
                        'student_1': w['name'],
                        'student_2': wo['name'],
                        'specialty': key[0],
                        'block': key[1],
                        'student_1_contact': w['phone'],
                        'student_2_contact': wo['phone'],
                        'student_1_location': w['location'],
                        'student_2_location': wo['location']
                    })
    return matches

def find_students_with_highlight(students, desired_specialty, desired_block):
    candidates = []
    for s in students:
        if s['specialty'].lower() == desired_specialty.lower() and s['block'].lower() == desired_block.lower():
            priority = categorize_candidate(s['trade_status'])  # Will handle "no_trade" as low priority
            candidates.append({
                'name': s['name'],
                'phone': s['phone'],
                'location': s['location'],
                'trade_status': s['trade_status'],
                'priority': priority
            })
    return candidates


# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files.get('file')
#         if not file:
#             flash('No file selected', 'error')
#             return redirect(request.url)
#
#         try:
#             # Use pandas to read Excel or CSV based on file extension
#             if file.filename.endswith('.xlsx'):
#                 df = pd.read_excel(file)
#             elif file.filename.endswith('.csv'):
#                 df = pd.read_csv(file)
#             else:
#                 flash('Unsupported file type. Upload .xlsx or .csv only.', 'error')
#                 return redirect(request.url)
#
#             # Expected columns: name, phone, specialty, block, location, trade_status
#             required_cols = {'name', 'phone', 'specialty', 'block', 'location', 'trade_status'}
#             if not required_cols.issubset(set(df.columns.str.lower())):
#                 flash(f'Missing required columns. Must include: {", ".join(required_cols)}', 'error')
#                 return redirect(request.url)
#
#             # Normalize column names to lower case for consistency
#             df.columns = df.columns.str.lower()
#
#             count = 0
#             for _, row in df.iterrows():
#                 # Basic row validation
#                 if pd.isna(row['name']) or pd.isna(row['phone']):
#                     continue  # skip incomplete rows
#
#                 # Check if student already exists, update if so
#                 existing = next((s for s in students if s['name'].lower() == str(row['name']).lower()), None)
#                 new_data = {
#                     'name': str(row['name']),
#                     'phone': str(row['phone']),
#                     'specialty': str(row['specialty']),
#                     'block': str(row['block']),
#                     'location': str(row['location']),
#                     'trade_status': str(row['trade_status']).lower()
#                 }
#                 if existing:
#                     existing.update(new_data)
#                 else:
#                     students.append(new_data)
#                 count += 1
#
#             flash(f'Successfully imported {count} records!', 'success')
#             return redirect(url_for('home'))
#
#         except Exception as e:
#             flash(f'Error processing file: {e}', 'error')
#             return redirect(request.url)
#
#     return render_template('upload.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ''
    if request.method == 'POST':
        # Get form data
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        specialty = request.form['specialty'].strip()
        block = request.form['block'].strip()
        location = request.form['location'].strip()
        status = request.form['trade_status']

        if not all([name, phone, specialty, block, location]):
            message = 'Please fill in all fields.'
        else:
            existing = next((s for s in students if s['name'].lower() == name.lower()), None)
            if existing:
                existing.update({
                    'phone': phone,
                    'specialty': specialty,
                    'block': block,
                    'location': location,
                    'trade_status': status
                })
                message = f'Updated info for {name}.'
            else:
                students.append({
                    'name': name,
                    'phone': phone,
                    'specialty': specialty,
                    'block': block,
                    'location': location,
                    'trade_status': status
                })
                message = f'Added new student {name}.'

    matches = find_matches(students)
    return render_template('index.html', students=students, matches=matches, message=message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    search_specialty = ''
    search_block = ''
    if request.method == 'POST':
        search_specialty = request.form['desired_specialty'].strip()
        search_block = request.form['desired_block'].strip()
        results = find_students_with_highlight(students, search_specialty, search_block)

    return render_template('search.html', results=results, specialty=search_specialty, block=search_block)

if __name__ == '__main__':
    app.run(debug=True)