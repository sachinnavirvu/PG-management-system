from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    id_number = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(15))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            error = 'Username already exists'
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/add_tenant_form')
def add_tenant_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_tenant.html')

@app.route('/add', methods=['POST'])
def add_tenant():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    id_number = request.form['id_number']
    age = request.form['age']
    email = request.form['email']
    address = request.form['address']
    phone_number = request.form['phone_number']
    new_tenant = Tenant(name=name, id_number=id_number, age=age, email=email, address=address, phone_number=phone_number)
    db.session.add(new_tenant)
    
    

    db.session.commit()
    return redirect(url_for('tenant_list'))

@app.route('/tenant_list')
def tenant_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tenants = Tenant.query.all()
    return render_template('tenant_list.html', tenants=tenants)

@app.route('/delete/<int:id>')
def delete_tenant(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tenant = Tenant.query.get_or_404(id)
    db.session.delete(tenant)
    db.session.commit()
    return redirect(url_for('tenant_list'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_tenant(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tenant = Tenant.query.get_or_404(id)
    if request.method == 'POST':
        tenant.name = request.form['name']
        tenant.id_number = request.form['id_number']
        tenant.age = request.form['age']
        tenant.email = request.form['email']
        tenant.address = request.form['address']
        tenant.phone_number = request.form['phone_number']
        db.session.commit()
        return redirect(url_for('tenant_list'))
    return render_template('update.html', tenant=tenant)

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/search', methods=['POST'])
def search_tenant():
    id_number = request.form['id_number']
    print(f"Searching for tenant with ID number: {id_number}")  # Debugging statement
    tenant = Tenant.query.filter_by(id_number=id_number).first()
    if tenant:
        print(f"Tenant found: {tenant.name}")
    else:
        print("Tenant not found")
    return render_template('search_result.html', tenant=tenant)

# Initialize chat_state dictionary
chat_state = {}
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()
        user_id = request.remote_addr  
        user_message = data['message']

        if user_id not in chat_state:
            chat_state[user_id] = {'step': 0, 'data': {}}

        state = chat_state[user_id]

        if user_message == '1' and state['step'] == 0:
            state['step'] = 1
            return jsonify({'response': "Your name please."})
        elif state['step'] == 1:
            state['data']['name'] = user_message
            state['step'] = 2
            return jsonify({'response': "Your age please."})
        elif state['step'] == 2:
            state['data']['age'] = user_message
            state['step'] = 3
            return jsonify({'response': "Your email please."})
        elif state['step'] == 3:
            state['data']['email'] = user_message
            state['step'] = 4
            return jsonify({'response': "Your address please."})
        elif state['step'] == 4:
            state['data']['address'] = user_message
            state['step'] = 5
            return jsonify({'response': "Your phone number please."})
        elif state['step'] == 5:
            state['data']['phone_number'] = user_message
            chat_state.pop(user_id)
            return jsonify({'response': store_information(state['data'])})
        elif user_message == '2':
            food_menu = """
            <h3>Here is the food menu:</h3>
            <ul>
                <li><strong>Monday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Vegetables pallav</li>
                        <li><strong>Lunch:</strong> Rice and sambhar</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Tuesday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Idli Sambhar</li>
                        <li><strong>Lunch:</strong> Rice and sambhar with vegetable palya</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Wednesday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Lemon rice</li>
                        <li><strong>Lunch:</strong> Rice and sambhar with papad</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Thursday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Dosa</li>
                        <li><strong>Lunch:</strong> Rice and sambhar</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Friday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Pulihora</li>
                        <li><strong>Lunch:</strong> Rice and sambhar</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Saturday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Puri with dal</li>
                        <li><strong>Lunch:</strong> Rice and sambhar</li>
                        <li><strong>Dinner:</strong> Chapathi with curry, rice and sambhar, with curd</li>
                    </ul>
                </li>
                <li><strong>Sunday</strong>
                    <ul>
                        <li><strong>Tiffen:</strong> Rice bath</li>
                        <li><strong>Lunch:</strong> Rice and sambhar</li>
                        <li><strong>Dinner:</strong> Non Veg</li>
                    </ul>
                </li>
            </ul>"""
            return jsonify({'response': food_menu})
        elif user_message == '3':
            pg_rules = """
            <h3>PG Rules:</h3>
            <ul>
                <li>No smoking inside the premises</li>
                <li>Visitors allowed only during visiting hours</li>
                <li>Maintain cleanliness</li>
                <li>No loud noises after 10 PM</li>
            </ul>"""
            return jsonify({'response': pg_rules})
        
        elif user_message == '4':
            payment_option = """
            <h3>Payment Option:</h3>
            <p>Please scan the following QR code to make your payment:</p>
            <div class='qr-code-container'>
                <img src='/static/qrcode.png' alt='QR Code' class='qr-code'>
            </div>"""
            return jsonify({'response': payment_option})
        else:
            return jsonify({'response': "Thank you for your message!"})
    else:
        return render_template('chat.html', bot_response='')

def store_information(data):
    name = data.get('name')
    age = int(data.get('age'))
    email = data.get('email')
    address = data.get('address')
    phone_number = data.get('phone_number')

    new_tenant = Tenant(name=name, age=age, email=email, address=address, phone_number=phone_number)
    db.session.add(new_tenant)
    db.session.commit()
    return f"Information about {name} has been stored successfully! Your room is booked."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
