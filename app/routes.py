from app import app
from flask import Flask, render_template, abort, url_for
from markupsafe import escape, Markup

@app.route('/')             #Startseite mit Liste aller Tiere
def index():
    
    return render_template('index.html', pets=pets)     #Übergebe dem Template index.html die Variable pets

        

@app.route('/login')        #Login-Seite
def login():
    
    obrigkeit = '''
    <!doctype html>
    <html lang="de">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Login</title>
    </head>
    <body>
        <h1>Hier findet sich - irgendwann in Zukunft - die Login-Seite</h1> 
    '''

    fußvolk = '''
    <h2>Vielleicht findet sich hier aber auch das Elixir zur Nasenhaarentfernung UND Nasenhaarhinzuführung!!!</h2>
    '''
    userinput1 = "<script>alert('Kaufen Sie heute Ihr exklusives Starterpaket Nasenhaartonikum!!! Buy 1 Pay 2!!!');</script>" #not escaped Userinput
    userinput2 = "Ich bin die traurige escaped Message: <script>alert('Kaufen Sie heute Ihr exklusives Starterpaket Nasenhaartonikum!!! Buy 1 Pay 2!!!');</script>" #escaped Userinput

    output = Markup(obrigkeit) + Markup(userinput1) + escape(userinput2) + Markup(fußvolk)
    return output

@app.route('/register')     #Seite zur Account-Erstellung
def register():
    return "Hier können Sie sich registrieren."

@app.route('/logout')       #Null, aber braucht man für den Logout
def logout():
    return "Hier werden Sie abgemeldet."

@app.route('/admin')        #Admin-Bereich
def admin():
    
    # return "Hier findet sich später das Admin-Dashboard."
    return render_template('admin.html', user = user)

@app.route('/edit_user/<int:user_id>')    #Bearbeiten eines Benutzers
def edit_user(user_id):
    return "Hier findet sich die Nutzerbearbeitung."

@app.route('/delete_user/<int:user_id>')    #Null, braucht man fürs Löschen eines Nutzers
def delete_user(user_id):
    return "Falls man mal einen Nutzer löschen muss."

@app.route('/pet/<int:pet_id>')             #Zeigt die Details eines Tieres an
def pet(pet_id):
    #Daten anhand der id raussuchen
    pet_details = None
    for p in pets:
        if p['pet_id'] == pet_id:
            pet_details = p
            break

    if pet_details is None:
        abort(404)
    
    else:
        return render_template('pet_details.html', pet = pet_details)

@app.route('/pet/<int:pet_id>/edit')        #Seite zum Bearbeiten eines Tieres
def pet_edit(pet_id):
    return "Die Tier-Bearbeitungs-Seite."

@app.route('/pet/<int:pet_id>/delete')      #Null, zum Löschen eines Tiers
def delete_pet(pet_id):
    return "Falls man mal ein Tier löschen muss."

@app.route('/pet/<int:pet_id>/borrow')      #Null, zum Ausleihen
def borrow_pet(pet_id):
    return "Wird benötigt wenn man ein Tier ausleihen möchte."

@app.route('/pet/<int:pet_id>/return')      #Null, für die Rückgabe
def return_pet(pet_id):
    return "Wird für die Rückgabe benötigt."

@app.route('/pet-management/<int:user_id>')               #Verwaltung eigener und geliehener Tiere
def pet_management(user_id):
    #Abgleich mit Tieren als Halter/Ausleiher
    own_pets = []
    borrowed_pets = []
    for p in pets:
        if p['owner_id'] == user_id:
            own_pets.append(p)
        elif p['borrower_id'] == user_id:
            borrowed_pets.append(p)
    
    vorhanden = False
    for u in user:
        if u['user_id'] == user_id:
            vorhanden = True
            break
    if vorhanden:
        return render_template('pet-management.html', own_pets=own_pets, borrowed_pets=borrowed_pets)

    else:
        abort(404)

##################################################################

# @app.route('/pet-management/<int:user_id>')
# def pet_management(user_id):

#     #Abgleich mit Tieren als Halter/Ausleiher
#         own_pets = []
#         borrowed_pets = []
#         for p in pets:
#             if p['owner_id'] == user_id:
#                 own_pets.append(p)
#             elif p['borrower_id'] == user_id:
#                 borrowed_pets.append(p)

#         html = f"""<!DOCTYPE html>
#     <html lang="de">
#     <head>
#     <meta charset="UTF-8">
#     <title>Tierverwaltung von {escape(user_id)}</title>
#     </head>
#     <body>
#     <a href="/">Startseite</a>

#     <h1>Tierverwaltung von Nutzer {escape(user_id)}</h1>

#     <div class="pet-list">
#         <h2>Hier findest du deine Haustiere:</h2>
#         <a href="/pet/new/{escape(user_id)}">Neuen Freund anlegen</a>
#         <br><br>
#         <table>
#             <tr>
#                 <th>Name</th>
#                 <th>Tierart</th>
#                 <th>Verfügbarkeit</th>
#                 <th>Aktionen</th>
#             </tr>
#             """
        
#         for p in own_pets:
#             html += "<tr>"
#             html += f"<td>{escape(p['name'])}</td>"
#             html += f"<td>{escape(p['animal_type'])}</td>"
#             if p['borrower_id'] is None:
#                 html += "<td>verfügbar</td>"
#             else:
#                 html += "<td>ausgeliehen</td>"
#             html += f"<td><a href='{url_for('pet_edit', pet_id=p['pet_id'])}'>Bearbeiten</a> <a href='{url_for('pet', pet_id=p['pet_id'])}'>Details</a></td>"
#             html += "</tr>"


#         html += """
        
#         </tr>
#         </table>

#         <h2>Hier findest du deine ausgeliehenen Haustiere:</h2>

#         <table>
#             <tr>
#                 <th>Name</th>
#                 <th>Tierart</th>
#                 <th>Besitzer-ID</th>
#                 <th>Aktionen</th>
#             </tr>
            
#         """
        
#         for p in borrowed_pets:
#             html += "<tr>"
#             html += f"<td>{escape(p['name'])}</td>"
#             html += f"<td>{escape(p['animal_type'])}</td>"
#             html += f"<td>{escape(p['owner_id'])}</td>"
#             html += f"<td><a href='{url_for('pet', pet_id=p['pet_id'])}'>Details</a></td>"
#             html += "</tr>"

#         html += """

#         </tr>
#         </table
#         </div>
#         </body>
#         </html>

#         """

#         return html

##################################################################

@app.route('/pet/new/<int:user_id>')                   #Seite zum Anlegen neuer Tiere
def pet_new(user_id):
    return "Wenn ein neues Tier angelegt wird, dann hier."

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
     'borrower_id': None,
     'image': 'bilder/fiffi.png'},

    {'pet_id': 2,
     'name': 'Herr Miezemann',
     'description': 'Philosophiert gern über den Sinn leerer Dosen.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': None,
     'image': 'bilder/herrmiezemann.png'},

    {'pet_id': 3,
     'name': 'Luna',
     'description': 'Verfolgt ihren eigenen Schatten mit religiösem Eifer.',
     'animal_type': 'dog',
     'owner_id': 1,
     'borrower_id': 3,
     'image': 'bilder/luna.png'},

    {'pet_id': 4,
     'name': 'Pixel',
     'description': 'Hat einmal auf die Tastatur gepinkelt und denkt, sie programmiert jetzt.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': None,
     'image': 'bilder/pixel.png'},

    {'pet_id': 5,
     'name': 'Wuffbert',
     'description': 'Liebt es, Netflix zu spoilern, bevor du’s siehst.',
     'animal_type': 'dog',
     'owner_id': 3,
     'borrower_id': None,
     'image': 'bilder/wuffbert.png'},

    {'pet_id': 6,
     'name': 'Mausolini',
     'description': 'Winzig, aber führt ein strenges Regime in der Küche.',
     'animal_type': 'cat',
     'owner_id': 2,
     'borrower_id': 4,
     'image': 'bilder/mausolini.png'},

    {'pet_id': 7,
     'name': 'Bella',
     'description': 'Hat mehr Instagram-Follower als du.',
     'animal_type': 'dog',
     'owner_id': 4,
     'borrower_id': None,
     'image': 'bilder/bella.png'},

    {'pet_id': 8,
     'name': 'Professor Flausch',
     'description': 'Schläft tagsüber, korrigiert nachts deine Lebensentscheidungen.',
     'animal_type': 'cat',
     'owner_id': 3,
     'borrower_id': None,
     'image': 'bilder/professorflausch.png'},

    {'pet_id': 9,
     'name': 'Rex',
     'description': 'Liebt Stöckchen, aber hasst, wenn sie physikalisch korrekt fliegen.',
     'animal_type': 'dog',
     'owner_id': 1,
     'borrower_id': 2,
     'image': 'bilder/rex.png'},

    {'pet_id': 10,
     'name': 'Whiskerstein',
     'description': 'Hat eine tiefgehende Feindschaft mit dem Staubsauger entwickelt.',
     'animal_type': 'cat',
     'owner_id': 4,
     'borrower_id': None,
     'image': 'bilder/whiskerstein.png'}
]

####################################

# Temporäre Nutzerliste

user = [

    {'user_id':     1,
     'name':        'Ventura',
     'password':    'password',
     'group':       'admin'},
    
    {'user_id':     2,
     'name':        'Winfried',
     'password':    'password',
     'group':       'user'},

    {'user_id':     3,
     'name':        'Kunigunde',
     'password':    'password',
     'group':       'user'},
    
    {'user_id':     4,
     'name':        'Wilbald',
     'password':    'password',
     'group':       'user'},

]