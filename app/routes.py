from app import app
from flask import Flask, render_template
from markupsafe import escape, Markup

@app.route('/')             #Startseite mit Liste aller Tiere
def index():
    
    return render_template('index.html', pets=pets)     #Übergebe dem Template index.html die Variable pets

        

@app.route('/login')        #Login-Seite
def login():
    pass

@app.route('/register')     #Seite zur Account-Erstellung
def register():
    pass

@app.route('/logout')       #Null, aber braucht man für den Logout

@app.route('/admin')        #Admin-Bereich
def admin():
    pass

@app.route('/edit_user')    #Bearbeiten eines Benutzers
def edit_user():
    pass

@app.route('/delete_user/<int:user_id>')    #Null, braucht man fürs Löschen eines Nutzers
def delete_user():
    pass

@app.route('/pet/<int:pet_id>')             #Zeigt die Details eines Tieres an
def pet(pet_id):
    #die Daten anhand der id raussuchen
    pet_details = None
    for p in pets:
        if p['pet_id'] == pet_id:
            pet_details = p
            break

    if pet_details is None:
        return render_template('404.html'), 404
    
    else:
        return render_template('pet_details.html', pet = pet_details)

@app.route('/pet/<int:pet_id>/edit')        #Seite zum Bearbeiten eines Tieres
def pet_edit():
    pass

@app.route('/pet/<int:pet_id>/delete')      #Null, zum Löschen eines Tiers
def delete_pet():
    pass

@app.route('/pet/<int:pet_id>/borrow')      #Null, zum Ausleihen
def borrow_pet():
    pass

@app.route('/pet/<int:pet_id>/return')      #Null, für die Rückgabe
def return_pet():
    pass

@app.route('/pet-management')               #Verwaltung eigener und geliehener Tiere
def pet_management():
    pass

@app.route('/pet/new')                      #Seite zum Anlegen neuer Tiere
def pet_new():
    pass

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

###############################################

# Liste mit Test-Haustieren

pets = [

    {'pet_id': 1,
     'name': 'Fiffi',
     'description': 'Sieht nett aus, ist es aber nicht!',
     'animal_type': 'dog',
     'owner_id': 1,
     'borrower_id': None},

    {'pet_id': 2,
     'name': 'Herr Miezemann',
     'description': 'Philosophiert gern über den Sinn leerer Dosen.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': None},

    {'pet_id': 3,
     'name': 'Luna',
     'description': 'Verfolgt ihren eigenen Schatten mit religiösem Eifer.',
     'animal_type': 'dog',
     'owner_id': 1,
     'borrower_id': 3},

    {'pet_id': 4,
     'name': 'Pixel',
     'description': 'Hat einmal auf die Tastatur gepinkelt und denkt, sie programmiert jetzt.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': None},

    {'pet_id': 5,
     'name': 'Wuffbert',
     'description': 'Liebt es, Netflix zu spoilern, bevor du’s siehst.',
     'animal_type': 'dog',
     'owner_id': 3,
     'borrower_id': None},

    {'pet_id': 6,
     'name': 'Mausolini',
     'description': 'Winzig, aber führt ein strenges Regime in der Küche.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': 4},

    {'pet_id': 7,
     'name': 'Bella',
     'description': 'Hat mehr Instagram-Follower als du.',
     'animal_type': 'dog',
     'owner_id': 4,
     'borrower_id': None},

    {'pet_id': 8,
     'name': 'Professor Flausch',
     'description': 'Schläft tagsüber, korrigiert nachts deine Lebensentscheidungen.',
     'animal_type': 'cat',
     'owner_id': 3,
     'borrower_id': None},

    {'pet_id': 9,
     'name': 'Rex',
     'description': 'Liebt Stöckchen, aber hasst, wenn sie physikalisch korrekt fliegen.',
     'animal_type': 'dog',
     'owner_id': 1,
     'borrower_id': 2},

    {'pet_id': 10,
     'name': 'Whiskerstein',
     'description': 'Hat eine tiefgehende Feindschaft mit dem Staubsauger entwickelt.',
     'animal_type': 'cat',
     'owner_id': 4,
     'borrower_id': None}
]

user = [

    {'user_id':     1,
     'password':    'password'},
    
    {'user_id':     2,
     'password':    'password'},

    {'user_id':     3,
     'password':    'password'},
    
    {'user_id':     4,
     'password':    'password'}

]