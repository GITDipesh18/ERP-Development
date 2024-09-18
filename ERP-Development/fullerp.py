from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response,Response
from flask_mail import Mail, Message
import csv
from flask import Flask, jsonify
import os
from flask import Flask, render_template, request, redirect, url_for,send_file,session
from urllib.parse import unquote, quote
import csv
from num2words import num2words
from werkzeug.security import check_password_hash, generate_password_hash




app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key for session management




USER_FILE = 'users.csv'
def load_users():
    users = []
    try:
        with open(USER_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError:
        pass
    return users

def get_user(username):
    users = load_users()
    for user in users:
        if user['username'] == username:
            return user
    return None



# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'shelardipesh18@gmail.com'
app.config['MAIL_PASSWORD'] = 'dqaz kdob xsyt wvug'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Add enumerate to the Jinja2 environment
app.jinja_env.globals.update(enumerate=enumerate)



# Dummy data structure to simulate storage (replace with database integration)
global indents
indents = []

# Initialize CSV files with headers if they don't exist
def initialize_csv_files():
    if not os.path.isfile('indents.csv'):
        with open('indents.csv', mode='w', newline='') as file:
            headers = ['Indent Number', 'Date', 'Department', 'Project_Name', 'Initiated By', 'Store', 'Manager', 'Director']
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

    if not os.path.isfile('items.csv'):
        with open('items.csv', mode='w', newline='') as file:
            headers = ['Indent Number', 'Item Code', 'Type of Item', 'Item with Specification', 'To be Used', 'Required By', 'Quantity', 'UDM']
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
    
    if not os.path.isfile('payment_advices.csv'):
        with open('payment_advices.csv', mode='w', newline='') as file:
            headers = ['Date', 'Vendor Name', 'Project Name', 'PO No.', 'Amount', 'Mode of Payment', 'Terms of Payment', 'Nature of Payment', 'Remarks',
                      'Prepared By', 'Initiated By', 'Checked By', 'Authorised By', 'Approved By']
            writer = csv.DictWriter(file, fieldname=headers)
            writer.writeheader()

    if not os.path.isfile('NEWGRN.csv'):
        with open('NEWGRN.csv', mode='w', newline='') as file:
            headers = ['GRN Number', 'PO No.', 'GRN Date', 'Vendor', 'Delivery Date', 'Item Code', 'Quantity', 'Unit Price', 'Total Price']
            writer = csv.DictWriter(file, fieldname=headers)
            writer.writeheader()


# Load existing indents and items from CSV files if they exist
def load_from_csv():
    initialize_csv_files()
    indents.clear()  # Clear existing data to prevent duplication
    with open('indents.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            indent = {
                'indent_number': row['Indent Number'],
                'date': row['Date'],
                'department': row['Department'],
                'project_name': row['Project Name'],  # New field
                'initiated_by': row['Initiated By'],
                'store': row['Store'],
                'manager': row['Manager'],
                'director': row['Director'],
                'items': []
            }
            indents.append(indent)

    with open('items.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for indent in indents:
                if indent['indent_number'] == row['Indent Number']:
                    item = {
                        'indent_number': row['Indent Number'],
                        'item_code': row['Item Code'],
                        'type_of_item': row['Type of Item'],
                        'item_with_specification': row['Item with Specification'],
                        'to_be_used': row['To be Used'],
                        'required_by': row['Required By'],
                        'quantity': row['Quantity'],
                        'udm': row['UDM']
                    }
                    indent['items'].append(item)

# Save indents to CSV files
def save_to_csv():
    with open('indents.csv', mode='w', newline='') as file:
        headers = ['Indent Number', 'Date', 'Department', 'Project Name', 'Initiated By', 'Store', 'Manager', 'Director']
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for indent in indents:
            writer.writerow({
                'Indent Number': indent['indent_number'],
                'Date': indent['date'],
                'Department': indent['department'],
                'Project Name': indent['project_name'],  # New field
                'Initiated By': indent['initiated_by'],
                'Store': indent['store'],
                'Manager': indent['manager'],
                'Director': indent['director']
            })

    with open('items.csv', mode='w', newline='') as file:
        headers = ['Indent Number', 'Item Code', 'Type of Item', 'Item with Specification', 'To be Used', 'Required By', 'Quantity', 'UDM']
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for indent in indents:
            for item in indent['items']:
                writer.writerow({
                    'Indent Number': indent['indent_number'],
                    'Item Code': item['item_code'],
                    'Type of Item': item['type_of_item'],
                    'Item with Specification': item['item_with_specification'],
                    'To be Used': item['to_be_used'],
                    'Required By': item['required_by'],
                    'Quantity': item['quantity'],
                    'UDM': item['udm']
                })

# Initialize and load data from CSV files
load_from_csv()


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        print(f"User already logged in: {session['username']} with role {session['role']}")
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user_password(username, password)
        if user:
            session['username'] = username
            session['role'] = user['role']
            print(f"Login successful for {username} with role {user['role']}")
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

import csv

def check_user_password(username, password):
    with open('users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return {'username': row['username'], 'role': row['role']}
    return None

def check_role(required_role):
    user_role = session.get('role')
    return user_role == required_role or user_role == 'superadmin'

@app.before_request
def restrict_routes():
    if 'username' not in session:
        if request.endpoint not in ['login']:
            return redirect(url_for('login'))
    else:
        user_role = session.get('role')
        
        
        
        # Define routes and roles
        restricted_routes = {
            'add_items': ['team_emp_user','team_leader_user','procurement_user','store_user','high_authority'],
            'purchaseorder': 'procurement_user',
            'vendor': ['account_user', 'superadmin']
        }
        
        if request.endpoint in restricted_routes:
            required_roles = restricted_routes[request.endpoint]
            
            if isinstance(required_roles, str):
                # Single role check
                if user_role != required_roles and user_role != 'superadmin':
                    return "Unauthorized", 403
            elif isinstance(required_roles, list):
                # Multiple roles check
                if user_role not in required_roles and user_role != 'superadmin':
                    return "Unauthorized", 403


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
       
        
        

# Route for displaying the index.html page with a list of indents
@app.route('/index', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    load_from_csv()  # Ensure the latest data is loaded before rendering
    user_role = session.get('role')  # Get the user's role from the session
    return render_template('index.html', indents=indents,user_role=user_role)

INDENT_CSV_FILE = 'indents.csv'
def generate_indent_number():
    """Generate a new indent number based on the highest existing indent number in the CSV."""
    highest_indent_number = 0
    
    try:
        with open(INDENT_CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists
            
            for row in reader:
                indent_number = row[0]  # Assuming indent number is in the first column
                # Extract the numeric part of the indent number
                try:
                    number_part = int(indent_number.split('/')[-1])
                    if number_part > highest_indent_number:
                        highest_indent_number = number_part
                except (ValueError, IndexError):
                    continue  # Skip invalid or incorrectly formatted indent numbers
    
    except FileNotFoundError:
        pass  # If the file doesn't exist, start from 1
    
    # Generate the next indent number
    next_indent_number = highest_indent_number + 1
    return f'Indent/24-25/{next_indent_number:04d}'


# Route for displaying the add_items.html form for creating or editing an indent
@app.route('/add_items', methods=['GET', 'POST'])
def add_items():
    if request.method == 'POST':
        indent_number = request.form.get('indent_number')
        date = request.form.get('date')
        department = request.form.get('department')
        project_name = request.form.get('project_name')  # New field
        initiated_by = request.form.get('initiated_by')
        store = request.form.get('store')
        manager = request.form.get('manager')
        director = request.form.get('director')

        items = []
        item_codes = request.form.getlist('item_code[]')
        types_of_item = request.form.getlist('type_of_item[]')
        items_with_specification = request.form.getlist('item_with_specification[]')
        to_be_used = request.form.getlist('to_be_used[]')
        required_by = request.form.getlist('required_by[]')
        quantities = request.form.getlist('quantity[]')
        udms = request.form.getlist('udm[]')

        for i in range(len(item_codes)):
            item = {
                'item_code': item_codes[i],
                'type_of_item': types_of_item[i],
                'item_with_specification': items_with_specification[i],
                'to_be_used': to_be_used[i],
                'required_by': required_by[i],
                'quantity': quantities[i],
                'udm': udms[i]
            }
            items.append(item)

        if not date or not department or not items:
            return "Date, Department, and at least one Item are mandatory!"
        

        indent = get_indent_by_number(indent_number)
        if indent is None:
            # Create a new indent if it doesn't exist
            indent = {
                'indent_number': indent_number,
                'date': date,
                'department': department,
                'project_name': project_name,  # New field
                'initiated_by': initiated_by,
                'store': store,
                'manager': manager,
                'director': director,
                'items': items
            }
            indents.append(indent)
        else:
            # Update only the relevant fields based on user role
            user_role = session.get('role')  # Get the user's role from the session
            
            indent['date'] = date
            indent['department'] = department
            indent['project_name'] = project_name  # New field
            indent['items'] = items

            if user_role in ['team_leader_user','high_authority','superadmin']:
                indent['initiated_by'] = initiated_by
            if user_role in ['store_user', 'high_authority','superadmin']:
                indent['store'] = store
            if user_role in [ 'superadmin','high_authority']:
                indent['manager'] = manager
            if user_role in ['high_authority']:
                indent['director'] = director

        save_to_csv()
        load_from_csv()  # Reload the data to reflect the changes

        # Send emails for approval stages (if needed)
        # send_indent_email(indent)

        return redirect(url_for('index'))

    else:
        user_role = session.get('role')  # Get the user's role from the session
        indent_number = request.args.get('indent_number')
        indent = get_indent_by_number(indent_number)
        if indent is None:
            indent = {
                'indent_number': generate_indent_number(),
                'date': '',
                'department': '',
                'project_name': '',  # New field
                'initiated_by': 'Pending',
                'store': 'Pending',
                'manager': 'Pending',
                'director': 'Pending',
                'items': []
            }
            
        return render_template('add_items.html', indent=indent, user_role=user_role)

# Helper function to fetch indent details based on indent_number
def get_indent_by_number(indent_number):
    for indent in indents:
        if indent['indent_number'] == indent_number:
            return indent
    return None


# Route for removing an item from an indent
@app.route('/remove_item/<indent_number>/<int:item_index>', methods=['GET'])
def remove_item(indent_number, item_index):
    for indent in indents:
        if indent['indent_number'] == indent_number:
            if 0 <= item_index < len(indent['items']):
                indent['items'].pop(item_index)
                save_to_csv()
                load_from_csv()  # Reload the data to reflect the changes
                return redirect(url_for('add_items', indent_number=indent_number))
            else:
                return "Item index out of range!"
    return "Indent not found!"

# Route for deleting an indent
@app.route('/delete_indent', methods=['POST'])
def delete_indent():
    indent_number = request.form.get('indent_number')
    print(f"Deleting indent: {indent_number}")  # Debug print statement
    global indents
    indents = [indent for indent in indents if indent['indent_number'] != indent_number]
    save_to_csv()
    load_from_csv()  # Reload the data to reflect the changes
    return redirect(url_for('index'))

# Route for downloading indent details as a formatted document
@app.route('/download_indent', methods=['POST'])
def download_indent():
    indent_number = request.form.get('indent_number')
    indent = get_indent_by_number(indent_number)
    
    if indent:
        # Prepare data to pass to the download template
        return render_template('download_indent.html', 
                               format_no="1",  # Example values; replace with actual data
                               rev_no="A",
                               date_no="18-06-2024",
                               indent_no=indent['indent_number'],
                               department=indent['department'],
                               date=indent['date'],
                               items=indent['items'],
                               initiated_by=indent['initiated_by'],
                               store=indent['store'],
                               manager=indent['manager'],
                               director=indent['director'])
    else:
        return "Indent not found!"

# Route for downloading the formatted indent details
@app.route('/download/<indent_number>')
def download(indent_number):
    indent = get_indent_by_number(indent_number)
    if indent:
        rendered = render_template('download_indent.html', 
                                   format_no="1",  # Example values; replace with actual data
                                   rev_no="A",
                                   date_no="18-06-2024",
                                   department=indent['department'],
                                   date=indent['date'],
                                   items=indent['items']),
        response = make_response(rendered)
        response.headers['Content-Disposition'] = 'attachment; filename="Item_Details_Indent.csv"'
        return response
    else:
        return "Indent not found!"
    
from flask import url_for

def send_indent_email(indent):
    recipients = ['shelardipesh18@gmail.com', 'pratiksunilbhirud@gmail.com']
    subject = f"Indent Created: {indent['indent_number']}"
    
    # Generate the URL for the add_items route with indent_number as a query parameter
    add_items_url = url_for('add_items', indent_number=indent['indent_number'], _external=True)
    
    body = f"""
    Server Link: http://127.0.0.1:5000/
    Direct Link: {add_items_url}
    Indent Number: {indent['indent_number']}
    Date: {indent['date']}
    Department: {indent['department']}
    Initiated By: {indent['initiated_by']}
    Store: {indent['store']}
    Manager: {indent['manager']}
    Director: {indent['director']}
    Items:
    """
    for item in indent['items']:
        body += f"""
        - Item Code: {item['item_code']}
          Type of Item: {item['type_of_item']}
          Item with Specification: {item['item_with_specification']}
          To be Used: {item['to_be_used']}
          Required By: {item['required_by']}
          Quantity: {item['quantity']}
          UDM: {item['udm']}
        """
    
    msg = Message(subject, sender='shelardipesh18@gmail.com', recipients=recipients)
    msg.body = body
    mail.send(msg)








from urllib.parse import unquote

CSV_FILE = 'purchase_orders.csv'

def generate_po_number():
    """Generate a new PO number based on the highest existing PO number in the CSV."""
    highest_po_number = 0
    
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists
            
            for row in reader:
                po_number = row[0]  # Assuming PO number is in the first column
                # Extract the numeric part of the PO number
                try:
                    number_part = int(po_number.split('/')[-1])
                    if number_part > highest_po_number:
                        highest_po_number = number_part
                except (ValueError, IndexError):
                    continue  # Skip invalid or incorrectly formatted PO numbers
    
    except FileNotFoundError:
        pass  # If the file doesn't exist, start from 1
    
    # Generate the next PO number
    next_po_number = highest_po_number + 1
    return f'PADT/23-24/{next_po_number:04d}'


# Example usage
new_po_number = generate_po_number()
print(f'Generated PO Number: {new_po_number}')



def get_po_by_number(po_number):
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        return [row for row in reader if row[0] == po_number]

@app.route('/purchaseorder/<path:indent_number>/', methods=['GET', 'POST'])
def purchaseorder(indent_number):
    decoded_indent_number = unquote(indent_number)
    
    # Check if 'po_number' query parameter is present
    po_number = request.args.get('po_number')
    po_details = None

    if po_number:
        # Fetch the purchase order details if po_number is provided
        po_details = get_po_by_number(po_number)
        if not po_details:
            return "Purchase Order not found!", 404

    if request.method == 'POST':
        # Handle form submission
        if po_details:
            po_number = po_details[0]  # Reuse the existing PO number
        else:
            po_number = generate_po_number()
            
        po_date = request.form['po_date']
        delivery_date = request.form['delivery_date']
        gst = request.form['gst']
        status = request.form['status']
        vendor = request.form['vendor']
        billShipToId = int(request.form['billShipTo'])  # Ensure billShipTo is converted to int
        descriptions = request.form.getlist('description[]')
        hsns = request.form.getlist('hsn[]')
        quantities = request.form.getlist('qty[]')
        rates = request.form.getlist('rate[]')
        gstAmounts = request.form.getlist('gstAmount[]')
        amounts = request.form.getlist('amount[]')
        grand_total = request.form['grand_total']
        amount_in_words = num2words(grand_total, to='currency', lang='en_IN')

        # Save data to CSV file
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            for i in range(len(descriptions)):
                writer.writerow([
                    po_number, decoded_indent_number, po_date, delivery_date, gst, status, vendor, 
                    billShipToId, descriptions[i], hsns[i], quantities[i], rates[i], gstAmounts[i], 
                    amounts[i], grand_total
                ])


        # Send email
        # Generate the URL for the purchaseorder route with po_number as a query parameter
        po_url = url_for('purchaseorder', indent_number=decoded_indent_number, po_number=po_number, _external=True)
        
        # Send email
        msg = Message('New Purchase Order Created', sender='shelardipesh18@gmail.com', recipients=['shelardipesh18@gmail.com'])
        
        msg.body = f"""
        PO Number: {po_number}
        Indent Number: {decoded_indent_number} 
        
        Direct PO Link: {po_url}
        Server Link: http://127.0.0.1:5000/
        """
        mail.send(msg)

        return redirect(url_for('poindex', indent_number=indent_number))
    
    
    # Render the purchase order form template
    items = []
    for t in indents:
        if indent_number == t['indent_number']:
            items.append( t['items'])  # Assuming 'items' is already a list
    
    user_role = session.get('role')  # Get the user's role from the session
    
    return render_template(
        'purchaseorder.html', 
        indent_number=decoded_indent_number, 
        items=items, 
        user_role=user_role,
        po_details=po_details,  # Pass the PO details if available
    )


def get_vendor_by_display_name(display_name):
    vendors = load_vendors()
    for vendor in vendors:
        if vendor['vendor_display_name'] == display_name:
            return vendor
    return None

@app.route('/download_po', methods=['POST'])
def download_po():
    po_number = request.form.get('po_number')
    po_list = get_po_by_number(po_number)  # Fetch the PO details
    
    if po_list:
        po = po_list[0]  # Get the first item from the list, which should be a dictionary-like list

        # Extract values from the PO list
        po_data = {
            'po_number': po[0],
            'po_date': po[2],
            'delivery_date': po[3],
            'gst': po[4],
            'status': po[5],
            'vendor': po[6],
            'bill_ship_to': po[7],
            'items': [
                {
                    'description': po[8],
                    'hsn': po[9],
                    'quantity': po[10],
                    'rate': po[11],
                    'gstAmount': po[12],
                    'amount': po[13]
                }
                for po in po_list[1:]
            ],
            'grand_total': po[14]
        }

        # Fetch address details
        address_id = po_data.get('bill_ship_to')
        addresses = {
            1: 'Paras Antidrone Technologies (Nerul)\nD-112, 1st Floor, TTC Industrial Area, Nerul MIDC, Nerul, Maharashtra,\n400706, India\nGSTIN: 27AAKCP3967C1Z7\nPhone: 02227629910, Fax: 02227629910\nEmail ID: info@parasantidrone.com',
            2: 'Paras Antidrone Technologies (Bengaluru)\n23, 2nd Floor, Sankey Square, Sankey Road, Lower Palace Orchards, Bengaluru - 560003\nGSTIN: 27AAKCP3967C1Z7\nTel: 080-23464139/4142, Fax: 02227629910\nEmail ID: info@parasantidrone.com'
        }
        address_details = addresses.get(int(address_id), '') if address_id else ''
        
        # Fetch vendor details
        vendor_display_name = po_data.get('vendor')
        vendor = get_vendor_by_display_name(vendor_display_name)
        if vendor:
            vendor_details = {
                'display_name': vendor_display_name,
                'address': vendor['address'],
                'gst_treatment': vendor['gst_treatment'],
                'contact_persons': vendor['contact_persons'],
                'vendor_phone': vendor['vendor_phone'],
                'vendor_email': vendor['vendor_email']
            }
        else:
            vendor_details = {
                'display_name': 'Vendor details not found',
                'address': '',
                'gst_treatment': '',
                'contact_persons': '',
                'vendor_phone': '',
                'vendor_email': ''
            }
        
        # Calculate totals
        total = sum(float(item['amount']) for item in po_data['items'])
        gst_total = sum(float(item['gstAmount']) for item in po_data['items'])
        
        # Render and prepare response
        rendered = render_template('download_po.html',
                                   po_number=po_data['po_number'],
                                   po_date=po_data['po_date'],
                                   delivery_date=po_data['delivery_date'],
                                   gst=po_data['gst'],
                                   status=po_data['status'],
                                   vendor=vendor_details,  # Pass vendor details to template
                                   address_details=address_details,  # Pass address details to template
                                   items=po_data['items'],
                                   amount=total,
                                   gstitem=gst_total,
                                   grandtotal=po_data['grand_total'])
        
        response = make_response(rendered)
        response.headers['Content-Disposition'] = f'attachment; filename="Purchase_Order_{po_number}.html"'
        return response
    else:
        return "Purchase Order not found!", 404
    


@app.route('/poindex/<path:indent_number>')
def poindex(indent_number):
    po_data = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        printed = []
        for row in reader:
            if len(row) > 5 and row[1] == indent_number:  # Ensure there are enough columns in the row
                if row[0] not in printed:  # Check if PO is not already printed
                    printed.append(row[0])
                    po_data.append({
                        'po_number': row[0],  # Assuming PO number is at index 0
                        'approval_status': row[5],  # Assuming approval status is at index 5
                        # Add other necessary fields as needed
                    })
    user_role = session.get('role')  # Get the user's role from the session
    print(f"User Role: {user_role}")  # Ensure the correct role is           
    return render_template('poindex.html', indent_number=indent_number, purchase_orders=po_data,user_role=user_role)

@app.route('/delete_po', methods=['POST'])
def delete_po():
    po_number = request.form['po_number']
    indent_number = request.form['indent_number']
    # user_role = session.get('role')  # Get the user's role from the session
    # print(f"User Role: {user_role}")  # Ensure the correct role is printed
    purchase_orders = []

    # Read the data from the CSV file
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        purchase_orders = list(reader)

    # Remove the purchase order based on PO number
    updated_purchase_orders = [po for po in purchase_orders if po[0] != po_number]

    # Write the updated data back to the CSV file
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_purchase_orders)
       
    return redirect(url_for('poindex', indent_number=indent_number))









from werkzeug.utils import secure_filename
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

VENDOR_FILE = 'vendors.csv'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_vendors():
    vendors = []
    try:
        with open(VENDOR_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vendors.append(row)
    except FileNotFoundError:
        pass
    return vendors

def save_vendors(vendors):
    with open(VENDOR_FILE, mode='w', newline='') as file:
        if vendors:
            writer = csv.DictWriter(file, fieldnames=vendors[0].keys())
            writer.writeheader()
            writer.writerows(vendors)

@app.route('/vendor')
def vendor():
    vendors = load_vendors()
    return render_template('index3.html', vendors=vendors)

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('document')
        if not files or any(file.filename == '' for file in files):
            flash('No selected file')
            return redirect(request.url)
        filenames = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)
            else:
                flash('Only PDF files are allowed!')
                return redirect(request.url)

        vendor = {
            'salutation': request.form['salutation'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'company_name': request.form['company_name'],
            'vendor_display_name': request.form['vendor_display_name'],
            'vendor_email': request.form['vendor_email'],
            'vendor_phone': request.form['vendor_phone'],
            'work_phone': request.form['work_phone'],
            'mobile': request.form['mobile'],
            'address': request.form['address'],
            'contact_persons': request.form['contact_persons'],
            'custom_fields': request.form['custom_fields'],
            'reporting_tags': request.form['reporting_tags'],
            'remarks': request.form['remarks'],
            'gst_treatment': request.form['gst_treatment'],
            'source_of_supply': request.form['source_of_supply'],
            'pan': request.form['pan'],
            'msme_registered': 'msme_registered' in request.form,
            'currency': request.form['currency'],
            'payment_terms': request.form['payment_terms'],
            'tds': request.form['tds'],
            'enable_portal': 'enable_portal' in request.form,
            'portal_language': request.form['portal_language'],
            'document': ','.join(filenames),
            'action': 'Pending'  # default action
        }

        # Check for mandatory fields
        for key, value in vendor.items():
            if key != 'msme_registered' and key != 'enable_portal' and not value:
                flash('All fields are mandatory except MSME Registered and Enable Portal!')
                return redirect(request.url)

        vendors = load_vendors()
        vendors.append(vendor)
        save_vendors(vendors)
        return redirect(url_for('vendor'))
    return render_template('add_vendor.html')

@app.route('/edit_vendor/<int:vendor>', methods=['GET', 'POST'])
def edit_vendor(vendor):
    vendors = load_vendors()
    if 0 <= vendor< len(vendors):
        if request.method == 'POST':
            # Update vendor details
            vendors[vendor]['salutation'] = request.form['salutation']
            vendors[vendor]['first_name'] = request.form['first_name']
            vendors[vendor]['last_name'] = request.form['last_name']
            vendors[vendor]['company_name'] = request.form['company_name']
            vendors[vendor]['vendor_display_name'] = request.form['vendor_display_name']
            vendors[vendor]['vendor_email'] = request.form['vendor_email']
            vendors[vendor]['vendor_phone'] = request.form['vendor_phone']
            vendors[vendor]['work_phone'] = request.form['work_phone']
            vendors[vendor]['mobile'] = request.form['mobile']
            vendors[vendor]['address'] = request.form['address']
            vendors[vendor]['contact_persons'] = request.form['contact_persons']
            vendors[vendor]['custom_fields'] = request.form['custom_fields']
            vendors[vendor]['reporting_tags'] = request.form['reporting_tags']
            vendors[vendor]['remarks'] = request.form['remarks']
            vendors[vendor]['gst_treatment'] = request.form['gst_treatment']
            vendors[vendor]['source_of_supply'] = request.form['source_of_supply']
            vendors[vendor]['pan'] = request.form['pan']
            vendors[vendor]['msme_registered'] = 'msme_registered' in request.form
            vendors[vendor]['currency'] = request.form['currency']
            vendors[vendor]['payment_terms'] = request.form['payment_terms']
            vendors[vendor]['tds'] = request.form['tds']
            vendors[vendor]['enable_portal'] = 'enable_portal' in request.form
            vendors[vendor]['portal_language'] = request.form['portal_language']
            # No update for document (PDF file) in edit
            save_vendors(vendors)
            return redirect(url_for('vendor'))
        return render_template('edit_vendor.html', vendor=vendors[vendor], index=vendor)
    flash('Vendor not found!')
    return redirect(url_for('vendor'))

@app.route('/update_vendor_action/<int:vendor>', methods=['POST'])
def update_vendor_action(vendor):
    action = request.form['action']
    vendors = load_vendors()
    if 0 <= vendor < len(vendors):
        vendors[vendor]['action'] = action
        save_vendors(vendors)
    return redirect(url_for('vendor'))


@app.route('/get_vendors')
def get_vendors():
    vendors = []
    with open('vendors.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            vendors.append({
                'salutation': row['salutation'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'company_name': row['company_name'],
                'vendor_display_name': row['vendor_display_name'],
                'vendor_email': row['vendor_email'],
                'vendor_phone': row['vendor_phone'],
                'work_phone': row['work_phone'],
                'mobile': row['mobile'],
                'address': row['address'],
                'contact_persons': row['contact_persons'],
                'custom_fields': row['custom_fields'],
                'reporting_tags': row['reporting_tags'],
                'remarks': row['remarks'],
                'gst_treatment': row['gst_treatment'],
                'source_of_supply': row['source_of_supply'],
                'pan': row['pan'],
                'msme_registered': row['msme_registered'],
                'currency': row['currency'],
                'payment_terms': row['payment_terms'],
                'tds': row['tds'],
                'enable_portal': row['enable_portal'],
                'portal_language': row['portal_language'],
                'document': row['document'],
                'action': row['action']
            })
    return jsonify(vendors)

@app.route('/get_addresses')
def get_addresses():
    addresses = [
        {
            'id': 1,
            'display_name': 'Paras Antidrone Technologies (Nerul)',
            'details': 'Paras Antidrone Technologies Private Limited\nD-112, 1st Floor, TTC Industrial Area, Nerul MIDC, Nerul, Maharashtra,\n400706, India\nGSTIN: 27AAKCP3967C1Z7\nPhone: 02227629910, Fax: 02227629910\nEmail ID: info@parasantidrone.com'
        },
        {
            'id': 2,
            'display_name': 'Paras Antidrone Technologies (Bengaluru)',
            'details': 'Paras Antidrone Technologies Private Limited\n23, 2nd Floor, Sankey Square, Sankey Road, Lower Palace Orchards, Bengaluru - 560003\nGSTIN: 27AAKCP3967C1Z7\nTel: 080-23464139/4142, Fax: 02227629910\nEmail ID: info@parasantidrone.com'
        }
    ]
    return jsonify(addresses) 





CSV_FILE1 = 'payment_advices.csv'

def generate_pa_number():
    """Generate a new PO number based on the highest existing Pa number in the CSV."""
    highest_pa_number = 0
    
    try:
        with open(CSV_FILE1, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists
            
            for row in reader:
                pa_number = row[0]  # Assuming PO number is in the first column
                # Extract the numeric part of the PO number
                try:
                    number_part = int(pa_number.split('/')[-1])
                    if number_part > highest_pa_number:
                        highest_pa_number = number_part
                except (ValueError, IndexError):
                    continue  # Skip invalid or incorrectly formatted PO numbers
    
    except FileNotFoundError:
        pass  # If the file doesn't exist, start from 1
    
    # Generate the next PO number
    next_pa_number = highest_pa_number + 1
    return f'PADT/23-24/{next_pa_number:04d}'

# Example usage
new_pa_number = generate_pa_number()
print(f'Generated PA Number: {new_pa_number}')

def get_pa_by_number(pa_number):
    # Example implementation for demonstration
    pa_data_list = []
    with open('payment_advices.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PA No.'] == pa_number:
                pa_data_list.append(row)
    return pa_data_list



@app.route('/paindex/<path:po_number>')
def paindex(po_number):
    payment_advices = []
    pas = []
    if os.path.exists(CSV_FILE1):
        with open(CSV_FILE1, newline='') as file:
            reader = csv.DictReader(file)
            payment_advices = list(reader)
    for pa in payment_advices:
        if pa['PO No.'] == po_number:
            pas.append(pa)
    user_role = session.get('role')  # Get the user's role from the session
    return render_template('paindex.html', payment_advices=pas, po_no=po_number,user_role=user_role)

@app.route('/create_pa', methods=['GET'])
def create_pa():
    po_number = request.args.get('po_number')
    pa_number = request.args.get('pa_number')  # Optional parameter for editing
    user_role = session.get('role')  # Get the user's role from the session

    if pa_number:
        # Fetch PA data for editing
        pa_data_list = get_pa_by_number(pa_number)
        
        # print("PA Data List:", pa_data_list)  # Debug print
        
        if isinstance(pa_data_list, list) and len(pa_data_list) > 0:
            pa_data = pa_data_list[0]  # Assuming there's only one match
            
            # Check if pa_data is in the expected dictionary format
            if isinstance(pa_data, dict):
                # Pre-fill form with PA details
                return render_template('create_pa.html',
                                       po_no=pa_data.get('PO No.', ''),
                                       pa_no=pa_data.get('PA No.', ''),
                                       date=pa_data.get('Date', ''),
                                       vendor_name=pa_data.get('Vendor Name', ''),
                                       project_name=pa_data.get('Project Name', ''),
                                       amount=pa_data.get('Amount', ''),
                                       mode_of_payment=pa_data.get('Mode of Payment', ''),
                                       terms_of_payment=pa_data.get('Terms of Payment', ''),
                                       nature_of_payment=pa_data.get('Nature of Payment', ''),
                                       remarks=pa_data.get('Remarks', ''),
                                       prepared_by=pa_data.get('Prepared By', ''),
                                       initiated_by=pa_data.get('Initiated By', ''),
                                       checked_by=pa_data.get('Checked By', ''),
                                       authorised_by=pa_data.get('Authorised By', ''),
                                       approved_by=pa_data.get('Approved By', ''),
                                       user_role=user_role)
            else:
                return "Payment Advice data format is incorrect.", 500
        else:
            return "Payment Advice not found or incorrect data format!", 404
    else:
        # Fetch PO data for creating new PA
        po_data_list = get_po_by_number(po_number)
        
        print("PO Data List:", po_data_list)  # Debug print
        
        if isinstance(po_data_list, list) and len(po_data_list) > 0:
            po_data = po_data_list[0]
            
            # Ensure po_data is in the expected list format and indices are correct
            if isinstance(po_data, list) and len(po_data) >= 7:
                vendor_name = po_data[6]  # Adjust index according to your CSV structure
                indent_number = po_data[1]  # Adjust index according to your CSV structure
                
                project_name = ""
                for indent1 in indents:
                    if indent_number == indent1['indent_number']:
                        project_name = indent1['project_name']
                        
                pa_no = generate_pa_number()  # Generate new PA number
                return render_template('create_pa.html', po_no=po_number, pa_no=pa_no,
                                       project_name=project_name, vendor_name=vendor_name, user_role=user_role)
            else:
                return "Purchase Order data format is incorrect.", 500
        else:
            return "Purchase Order not found or incorrect data format!", 404






@app.route('/save_pa', methods=['POST'])
def save_pa():
    # Gather the PA data from the form
    new_pa = {
        'PA No.': request.form['pa_no'],
        'Date': request.form['date'],
        'Vendor Name': request.form['vendor_name'],
        'Project Name': request.form['project_name'],
        'PO No.': request.form['po_no'],
        'Amount': request.form['amount'],
        'Mode of Payment': request.form['mode_of_payment'],
        'Terms of Payment': request.form['terms_of_payment'],
        'Nature of Payment': request.form['nature_of_payment'],
        'Remarks': request.form['remarks'],
        'Prepared By': request.form['prepared_by'],
        'Initiated By': request.form['initiated_by'],
        'Checked By': request.form['checked_by'],
        'Authorised By': request.form['authorised_by'],
        'Approved By': request.form['approved_by']
    }

    # Read existing PAs from the CSV file
    updated = False
    pa_list = []
    with open(CSV_FILE1, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for pa in reader:
            if pa['PA No.'] == new_pa['PA No.']:
                # If the PA exists, update the details
                pa = new_pa
                updated = True
            pa_list.append(pa)

    # If the PA was not found, add it as a new entry
    if not updated:
        pa_list.append(new_pa)

    # Write the updated list back to the CSV file
    with open(CSV_FILE1, 'w', newline='') as file:
        fieldnames = ['PA No.', 'Date', 'Vendor Name', 'Project Name', 'PO No.', 'Amount', 'Mode of Payment',
                      'Terms of Payment', 'Nature of Payment', 'Remarks', 'Prepared By', 'Initiated By',
                      'Checked By', 'Authorised By', 'Approved By']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pa_list)

    return redirect(url_for('paindex', po_number=new_pa['PO No.']))


@app.route('/download_pa', methods=['POST'])
def download_pa():
    pa_number = request.form.get('pa_number')
    pa_list = get_pa_by_number(pa_number)
    
    if pa_list:
        # Assuming you want the first PA record from the list
        pa = pa_list[0]
        
        rendered = render_template('paformat.html',
                                   pa_number=pa['PA No.'],
                                   date=pa['Date'],
                                   vendor=pa['Vendor Name'],
                                   project_name=pa['Project Name'],
                                   po_no=pa['PO No.'],
                                   amount=pa['Amount'],
                                   amount_words=num2words(pa['Amount']),
                                   mode=pa['Mode of Payment'],
                                   terms=pa['Terms of Payment'],
                                   nature=pa['Nature of Payment'],
                                   remarks=pa['Remarks'],
                                   prepared=pa['Prepared By'],
                                   initiated=pa['Initiated By'],
                                   checked=pa['Checked By'],
                                   authorised=pa['Authorised By'],
                                   approved=pa['Approved By'])
        
        response = make_response(rendered)
        response.headers['Content-Disposition'] = f'attachment; filename="Payment_Advice_{pa_number}.html"'
        return response
    else:
        return "Payment Advice not found!", 404

    
    
@app.route('/delete_pa', methods=['POST'])
def delete_pa():
    pa_number = request.form['pa_number']
    po_number = request.form['po_number']

    # Read the data from the CSV file
    with open('payment_advices.csv', 'r') as file:
        reader = csv.reader(file)
        payment_advices = list(reader)

    # Remove the payment advice based on PA number
    updated_payment_advices = [pa for pa in payment_advices if pa[0] != pa_number]

    # Write the updated data back to the CSV file
    with open('payment_advices.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_payment_advices)

    return redirect(url_for('paindex', po_number=po_number))











# Path to the GRN CSV file
GRN_FILE = 'GRNLIST.csv'
VENDORS_FILE = 'vendors.csv'

# Utility function to read CSV file and return unique GRNs
def read_grns(po_number):
    grns = {}
    if os.path.exists(GRN_FILE):
        with open(GRN_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['PO No.'] == po_number:
                    grn_number = row['GRN Number']
                    # Only keep the first entry for each GRN Number
                    if grn_number not in grns:
                        grns[grn_number] = row
    return list(grns.values())

@app.route('/grnindex', methods=['GET'])
def grnindex():
    po_number = request.args.get('po_number')
    grns = read_grns(po_number)
    return render_template('grnindex.html', po_number=po_number, grns=grns)


def generate_grn_number():
    """Generate a new PO number based on the number of existing entries in the CSV."""
    with open('GRNLIST.csv', 'r') as file:
        lines = file.readlines()
        return f'{len(lines) + 1:04d}'

import csv
import os

GRN_FILE = 'GRNitems.csv'
VENDORS_FILE = 'vendors.csv'
PURCHASE_ORDERS_FILE = 'purchase_orders.csv'

@app.route('/add_grn', methods=['GET', 'POST'])
def add_grn():
    po_number = request.args.get('po_number')
    if request.method == 'POST':
        grn_number = generate_grn_number()
        po_num = request.form['po_num']
        grn_date = request.form['grn_date']
        vendor = request.form.get('vendor', '')
        delivery_date = request.form['delivery_date']
        terms_of_payment = request.form['terms_of_payment']
        buyers_order_no = request.form['buyers_order_no']
        
        items = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        
        with open(GRN_FILE, mode='a', newline='') as file:
            fieldnames = ['GRN Number', 'PO No.', 'GRN Date', 'Vendor', 'Delivery Date', 'Terms of Payment', 'Buyer\'s Order No.', 'Description of Goods', 'Quantity']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            
            for item, quantity in zip(items, quantities):
                writer.writerow({
                    'GRN Number': grn_number,
                    'PO No.': po_num,
                    'GRN Date': grn_date,
                    'Vendor': vendor,
                    'Delivery Date': delivery_date,
                    'Terms of Payment': terms_of_payment,
                    'Buyer\'s Order No.': buyers_order_no,
                    'Description of Goods': item,
                    'Quantity': quantity
                })
        
        return redirect(url_for('grnindex', po_number=po_number))

    # Fetch items based on PO number
    items = []
    if os.path.exists(PURCHASE_ORDERS_FILE):
        with open(PURCHASE_ORDERS_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['PO Number'] == po_number:
                    items.append({
                        'description': row['Description'], 
                        'quantity': row['Quantity']
                    })

    vendors = []  # Populate this list as needed
    if os.path.exists(VENDORS_FILE):
        with open(VENDORS_FILE, newline='') as file:
            reader = csv.DictReader(file)
            vendors = list(reader)

    return render_template('add_grn.html', po_number=po_number, vendors=vendors, grn_number=generate_grn_number(), items=items)


# Utility function to get GRN by number
def get_grn_by_number(grn_number):
    grn_details = []
    with open(GRN_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['GRN Number'] == grn_number:
                grn_details.append(row)
    if grn_details:
        return grn_details
    return None

import csv

VENDOR_FILE = 'vendors.csv'

def get_vendor_by_display_name(vendor_display_name):
    with open(VENDOR_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['vendor_display_name'] == vendor_display_name:
                return row
    return None



@app.route('/download_grn/<encoded_grn_number>', methods=['GET'])
def download_grn(encoded_grn_number):
    grn_number = unquote(encoded_grn_number)
    print(f"Decoded GRN Number: {grn_number}")  # Debug statement

    grn_details = get_grn_by_number(grn_number)
    if grn_details:
        items = [{'description': row['Description of Goods'], 'quantity': row['Quantity']} for row in grn_details]
        total_quantity = sum(int(item['quantity']) for item in items)
        first_row = grn_details[0]
        
        # Fetch vendor details
        vendor_display_name = first_row['Vendor']
        vendor = get_vendor_by_display_name(vendor_display_name)
        if vendor:
            vendor_details = {
                'display_name': vendor_display_name,
                'address': vendor['address'],
                'gst_treatment': vendor['gst_treatment'],
                'contact_persons': vendor['contact_persons'],
                'vendor_phone': vendor['vendor_phone'],
                'vendor_email': vendor['vendor_email']
            }
        else:
            vendor_details = {
                'display_name': vendor_display_name,
                'address': 'N/A',
                'gst_treatment': 'N/A',
                'contact_persons': 'N/A',
                'vendor_phone': 'N/A',
                'vendor_email': 'N/A'
            }
        
        rendered = render_template('download_grn.html',
                                   grn_number=first_row['GRN Number'],
                                   po_number=first_row['PO No.'],
                                   grn_date=first_row['GRN Date'],
                                   vendor_details=vendor_details,  # Pass vendor details as a dictionary
                                   delivery_date=first_row['Delivery Date'],
                                   terms_of_payment=first_row['Terms of Payment'],
                                   buyers_order_no=first_row['Buyer\'s Order No.'],
                                   items=items,
                                   total_quantity=total_quantity
                                   )
        
        response = make_response(rendered)
        response.headers['Content-Disposition'] = f'attachment; filename="Goods_Receipt_Note_{grn_number}.html"'
        return response
    else:
        return "Goods Receipt Note not found!", 404
    
    
    
    
    
    

@app.route('/delete_grn/<grn_number>', methods=['POST'])
def delete_grn(grn_number):
    # Read all rows from the CSV file
    with open(GRN_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    # Write back rows except the one with the specified GRN number
    with open(GRN_FILE, mode='w', newline='') as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if row['GRN Number'] != grn_number:
                writer.writerow(row)
    
    # Redirect to the GRN index page with PO number
    po_number = request.form.get('po_number')  # Get PO number from form data
    return redirect(url_for('grnindex', po_number=po_number))


if __name__ == '__main__':
    app.run(debug=True)