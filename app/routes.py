import os
import mysql.connector
from app import app
from flask import Flask, render_template, abort, url_for, request, redirect, session, flash
from markupsafe import escape, Markup
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Angabe des Upload-Folders für die Profilbilder der Tiere
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'bilder')
# Größenlimit für die Bilder - 8MB
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024 
# Erlaubte Dateien für den Upload
allowed_extensions = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


#Wrapper für Login-Prüfung
def login_required(_):
    @wraps(_)
    def mcwrappenstein(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return _(*args, **kwargs)
    return mcwrappenstein


#Überprüfungsfunktion ob das hochgeladene File eine zulässige Datei ist, nötig für den Bildupload in pet_new()
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


#Funktion die eine Verbindung zur Datenbank aufbaut und per Return zur Verfügung stellt. 
def get_db_connection():            
    connection = mysql.connector.connect(
        host="localhost",
        user="adoptify",
        password="bananenboot",
        database="adoptify"
    )
    return connection


#Index-Seite - Verschlankt - Alle benötigten Infos in einem Abruf, ohne nachträgliches Filtern mittels Python/Jinja
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('''
                    select
                   p.pet_id,
                   p.name,
                   p.description,
                   p.animal_type,
                   p.owner_id,
                   p.image,
                   exists (
                   select 1
                   from borrowings b
                   where b.pet_id = p.pet_id
                   and b.active = 1
                   ) as is_borrowed
                   from pets p
                   order by p.pet_id
                   ''')
    
    pets = cursor.fetchall()
    connection.close()

    return render_template('index.html', pets=pets)


#Seite zum Login-Aufruf
@app.get('/login')        
def login_get():
    return render_template('login.html')


#Login-Submit
@app.post('/login')
def login_post():
    entered_username = request.form['username']
    entered_password = request.form['password']

    if not entered_username or not entered_password:
        flash("Bitte Benutzername und Passwort eingeben.", "error")
        return redirect(url_for('login_get'))

    #Verbindung zur Datenbank um eingegeben Konto-Daten zu überprüfen
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    select * from users
                   where name = %s
                   ''',
                   (entered_username,)
                   )
    user = cursor.fetchone()
    connection.close()

    if not user:
        flash("Benutzername oder Passwort nicht korrekt.", "error")
        return redirect(url_for('login_get'))
    
    stored = user['password']
    #check ob pw schon gehashed oder nicht mit werkzeug default sha256: "scrypt:..."
    is_hashed = stored.startswith("scrypt:")

    ok = False
    if is_hashed:
        ok = check_password_hash(stored, entered_password)
    
    else:
        ok = (stored == entered_password)
        if ok:
            #Passwort Migration des Altbestands starten
            new_hash = generate_password_hash(entered_password)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                            update users 
                            set password = %s 
                            where user_id = %s
                            ''',
                            (new_hash, user['user_id'])
                            )
            
            connection.commit()
            connection.close()
    
    if not ok:
        # also keine Übereinstimmung -> zurück zum login
        flash("Benutzer oder Password nicht korrekt.", "error")
        return redirect(url_for('login_get'))
    
    # Jetzt die Session setzen
    session.clear() #Session löschen, falls noch irgendwelche alten Daten drin sein könnten
    session['user_id'] = int(user['user_id'])
    session['name'] = user['name']
    session['role'] = user['role']

    flash(f"Du hast dich erfolgreich angemeldet {user['name']}!", "success")
    return redirect(url_for('index'))


#Seite zur Account-Erstellung Aufruf
@app.get('/register')     
def register_get():
    return render_template('register.html')


#Account-Erstellung - Submit
@app.post('/register')
def register_post():

    choosen_username = request.form['username']
    choosen_password = request.form['password']
    hashed_password = generate_password_hash(choosen_password)      # Muss noch von werkzeug.utils importiert werden

    #Datenbank-Verwurstung

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    insert into users 
                   (name, password) 
                   values (%s, %s)
                   ''', 
                   (choosen_username, hashed_password)
                   )
    connection.commit()

    #Abholen der user_id des gerade angelegten Nutzers
    cursor.execute('''
                    select user_id 
                   from users
                   where password = %s
                   and name = %s
                   ''',
                   (hashed_password, choosen_username)
                   )
    user_id = cursor.fetchone()
    connection.close()
    

    #Account-Infos in der Session speichern
    session['user_id'] = user_id
    session['username'] = choosen_username

    return redirect(url_for('index'))


#Null, aber braucht man für den Logout
@app.route('/logout')       
def logout():
    session.clear()

    flash("Du wurdest erfolgreich abgemeldet.", "success")
    return redirect(url_for('index'))


#User Management Dashboard
@app.route('/admin')
def admin():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''select
                   user_id, name, role
                   from users''')
    users = cursor.fetchall()
    connection.close()

    return render_template('admin.html', user=users)


#Bearbeiten eines Benutzers
@app.route('/edit_user/<int:user_id>')
def edit_user(user_id):
    return "Hier findet sich die Nutzerbearbeitung."


#Null, braucht man fürs Löschen eines Nutzers
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    return "Falls man mal einen Nutzer löschen muss."


# Pet-Details - Verschlankt - Nur noch ein Datensatz der aus der DB abgerufen wird.  
@app.route('/pet/<int:pet_id>')
def pet(pet_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    select
                   p.pet_id,
                   p.name,
                   p.description,
                   p.animal_type,
                   p.owner_id,
                   p.image,
                   exists (
                   select 1
                   from borrowings b
                   where b.pet_id = p.pet_id
                   and b.active = 1
                   ) as is_borrowed,
                   (
                   select b.borrower_id
                   from borrowings b
                   where b.pet_id = p.pet_id
                   and b.active = 1
                   limit 1
                   ) as borrower_id
                   from pets p
                   where p.pet_id = %s''',
                   (pet_id,) # execute möchte ein Tupel speisen, also vergesse er nicht ein Komma hinter der Variable, sonst rastet Python aus
                   )
    pet_details = cursor.fetchone()
    connection.close()

    return render_template('pet_details.html', pet=pet_details) 
    

# Tier Bearbeiten - Verschlankt - Daten mittels SQL vorsortiert
@app.route('/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def pet_edit(pet_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    select
                   name,
                   description,
                   animal_type,
                   owner_id
                   from pets
                   where pet_id = %s''',
                   (pet_id,)
                   )
    
    pet = cursor.fetchone() #V1
    connection.close()

    if request.method == 'POST':
        name = request.form['name']
        animal_type = request.form['animal_type']
        description = request.form['description']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
                        update pets
                       set name = %s,
                       animal_type = %s,
                       description = %s
                       where pet_id = %s''',
                       (name, animal_type, description, pet_id)
                       )
        connection.commit()
        connection.close()

        #Weiterleitung / Zurück zur Tier-Verwaltung
        return redirect(url_for('pet_management', user_id=pet['owner_id']))
    
    return render_template('pet_edit.html', pet=pet)


@app.route('/pet/<int:pet_id>/delete', methods=['GET', 'POST'])    
def delete_pet(pet_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    #Erst Dateiname vom Bild aus der DB holen
    cursor.execute('''
                    select owner_id, 
                   image
                   from pets
                   where pet_id = %s''',
                   (pet_id,)
                   )
    del_pet = cursor.fetchone()

    if not del_pet:
        connection.close()
        flash("Hm, hier stimmt was nicht.", "error")
        return redirect(url_for('index'))
    
    if del_pet['owner_id'] != session['user_id']: 
        connection.close()
        flash("Das ist nicht dein Tier, Finger weg!", "error")
        return redirect(url_for('pet', pet_id=pet_id))
    
    image_dateiname = del_pet['image']

    #Datensatz in DB löschen
    cursor.execute('''
                    delete from pets
                   where pet_id = %s''',
                   (pet_id,)
                   )

    connection.commit()
    connection.close()

    #Datei im Filesystem löschen - sofern vorhanden
    if image_dateiname:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_dateiname)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except OSError:
            pass

    flash("Eintrag und Dateien wurden gelöscht.", "success")
    return redirect(url_for('index'))


#Null, zum Ausleihen
@app.route('/pet/<int:pet_id>/borrow', methods=['GET', 'POST'])
def borrow_pet(pet_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Vorher überprüfen ob das Tier nicht eins von unseren ist... 
    cursor.execute('''
                    select case
                   when owner_id = %s then 0
                   else 1
                   end as origin
                   from pets 
                   where pet_id = %s
                   ''',
                   (session['user_id'], pet_id,)
                   )
    status = cursor.fetchone()

    if not status or status['origin'] == 0:
        flash("Du kannst dein eigenes Tier nicht ausleihen, Smartypants.", "error")
        return redirect(url_for('pet', pet_id=pet_id))

    if status:

        cursor.execute('''
                        insert into borrowings (pet_id, borrower_id)
                    values (%s, %s)
                    ''',
                    (pet_id, session['user_id'],)
                    )
    
        connection.commit()
        connection.close()

        flash("Tier erfolgreich ausgeliehen!", "success")
        return redirect(url_for('pet', pet_id=pet_id))


@app.route('/pet/<int:pet_id>/return', methods=['GET', 'POST'])
def return_pet(pet_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('''
                    update borrowings 
                   set active = 0
                   where pet_id = %s
                   and borrower_id = %s
                   and active = 1
                   ''', 
                   (pet_id, session['user_id'],)) #user_id temporär aus globaler Variable, später session_id
    
    connection.commit()
    returned = cursor.rowcount #zählt die tatsächlich veränderten Datensätze, wenn erfolgreich dann >= 1
    connection.close()

    if returned >= 1:
        flash("Tier wurde seinem Besitzer zurückgefaxt.", "success")
    elif returned == 0:
        flash("Hm, irgendwas stimmt hier nicht, bitte wende dich an den Betreiber", "error")

    return redirect(url_for('pet', pet_id = pet_id))


# Tierverwaltung - Verschlankt - Information direkt per SQL wie benötigt, statt mittels Python Loops after Loops...
@app.route('/pet-management')
def pet_management():
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    select
                        p.pet_id,
                        p.name,
                        p.animal_type,
                        case
                            when exists (
                                select 1
                                from borrowings b
                                where b.pet_id = p.pet_id
                                and b.active = 1
                                ) 
                                then 'verliehen'
                                else 'verfügbar'
                            end as status
                   from pets p
                   where p.owner_id = %s''',
                   (user_id,)
                   )
    
    own_pets = cursor.fetchall() #V1 für Übersicht meiner Tiere und nur diese o_^
    
    cursor.execute('''
                    select
                        p.pet_id,
                        p.name,
                        p.animal_type,
                        p.owner_id
                    from pets p
                    where pet_id in (
                    select pet_id
                    from borrowings b
                    where b.borrower_id = %s
                    and b.active = 1)''',
                    (user_id,)
                    )

    borrowed_pets = cursor.fetchall() #V2 für Übersicht meiner ausgeliehenen Tiere
    connection.close()

    return render_template('pet-management.html', own_pets=own_pets, borrowed_pets=borrowed_pets)


#Seite zum Anlegen neuer Tiere
@app.route('/pet/new', methods=['GET', 'POST'])
def pet_new():
    user_id = session['user_id']
    if request.method == 'POST':

        name = request.form['name']
        animal_type = request.form['animal_type']
        description = request.form['description']

        if not name.strip() or not animal_type.strip():
            flash("Bitte gib mindestens Namen & Tierart an!", "error")
            return render_template('pet_new.html')


        #Standardmäßig kein Bild
        image = None

        #Bildupload - die Verwirrung ist groß
        file = request.files['image']
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)

                #Ok, nochmal gucken ob der Ordner überhaupt existiert
                upload_folder = app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                #Als String abspeichern
                image = f"{filename}"
            
        #Speichern in der Datenbank
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
                        insert into pets (
                            name, animal_type, description, owner_id, image)
                            Values (%s, %s, %s, %s, %s)
                        ''', (name, animal_type, description, user_id, image)
                        )
        
        connection.commit()
        connection.close()


        #Weiterleitung / Zurück zur Tier-Verwaltung
        return redirect(url_for('pet_management'))

    else:
        return render_template('pet_new.html')


#Fallback auf die angelegte Fehlerseite
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

