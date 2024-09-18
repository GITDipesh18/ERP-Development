Po Route in flask application

CSV_FILE = 'purchase_orders.csv'

def generate_po_number():
    """Generate a new PO number based on the number of existing entries in the CSV."""
    with open(CSV_FILE, 'r') as file:
        lines = file.readlines()
        return f'PADT/23-24/{len(lines) + 1:04d}'


def get_po_by_number(po_number):
    with open(CSV_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        items = []
        for row in reader:
            if row and row[0] == po_number:  # Ensure the row is not empty and PO number is at index 0
                for i in range(8, len(row), 7):
                    if i + 6 < len(row):  # Ensure there are enough columns for items
                        items.append({
                            'description': row[i],
                            'hsn': row[i + 1],
                            'quantity': row[i + 2],
                            'rate': row[i + 3],
                            'gstAmount': row[i + 4],
                            'amount': row[i + 5]
                        })
        if items:  # Check if items list is not empty
            return {
                'po_number': row[0],
                'indent': row[1],
                'po_date': row[2],
                'delivery_date': row[3],
                'gst': row[4],
                'status': row[5],
                'vendor': row[6],
                'bill_ship_to': row[7],
                'items': items,
                'grand_total': row[-1]
            }
    return None


@app.route('/purchaseorder/<path:indent_number>/', methods=['GET', 'POST'])
def purchaseorder(indent_number):
    decoded_indent_number = unquote(indent_number)
    
    if request.method == 'POST':
        # Extract form data
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
        amount_in_words = num2words(grand_total, to='currency', lang='en_IND')
        
        
        # Save data to CSV file
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            for i in range(len(descriptions)):
                writer.writerow([
                    po_number, decoded_indent_number, po_date, delivery_date, gst, status, vendor, 
                    billShipToId, descriptions[i], hsns[i], quantities[i], rates[i], gstAmounts[i], 
                    amounts[i], grand_total
                ])
        
        return redirect(url_for('poindex', indent_number=indent_number))
    
    # Render the purchase order form template
    items = []  # You need to adjust this based on your data structure
    # For example, if indents is a list of dictionaries, adjust accordingly
    for t in indents:
        if indent_number == t['indent_number']:
            items.append(t['items'])
    
    
    user_role = session.get('role')  # Get the user's role from the session
    return render_template('purchaseorder.html', indent_number=decoded_indent_number, items=items, user_role=user_role)

def get_vendor_by_display_name(display_name):
    vendors = load_vendors()
    for vendor in vendors:
        if vendor['vendor_display_name'] == display_name:
            return vendor
    return None

    
    
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
    #logic here
       
    return redirect(url_for('poindex', indent_number=indent_number))

then below is purchaseorder.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='add_item_style.css') }}">
  
</head>
<body>

    <div class="header">
        <h4>PARAS ANTI-DRONE TECHNOLOGIES PVT</h4>
    </div>

    <div class="mainbox">
        <div class="menubar">
            <a href="#">HOME</a>
            <a href="#">PURCHASE</a>
            <a href="#">PRODUCTION</a>
            <a href="#">PROJECTS</a>
        </div>
        <div class="content">
          <div class="container-fluid mt-5">
            <h2 class="text-center my-4">PO Form for Indent {{ indent_number }}</h2>
            <form action="{{ url_for('purchaseorder', indent_number=indent_number, items=items) }}" method="post">
              <div class="mb-3">
                <label for="po_number" class="form-label">PO Number</label>
                <input type="text" class="form-control" id="po_number" name="po_number" value="PADT/23-24/0001" readonly>
              </div>
              <div class="mb-3">
                <label for="po_date" class="form-label">PO Date</label>
                <input type="date" class="form-control" id="po_date" name="po_date" required>
              </div>
              <div class="mb-3">
                <label for="delivery_date" class="form-label">Delivery Date</label>
                <input type="date" class="form-control" id="delivery_date" name="delivery_date" required>
              </div>
              <!-- Add a hidden input field for indent_number -->
              <div class="row mb-3">
                <div class="col-sm-4">
                  <label for="vendor" class="form-label">Select Vendor</label>
                  <br>
                  <select class="form-select" id="vendor" name="vendor">
                    <option value="">Select Vendor</option>
                  </select>
                </div>
                <div style="padding-left: 80px;">
                <div class="col-sm-4">
                  <label for="billShipTo" class="form-label">Select Address</label>
                  <select class="form-select" id="billShipTo" name="billShipTo">
                    <option value="">Select Address</option>
                  </select>
                </div>
                </div>
              </div>
                    <!-- Address selection -->
                    <div class="row mb-3">
                      <div class="col-sm-5">
                        <label for="vendorDetails" class="form-label">Vendor Details</label>
                        <textarea class="form-control" id="vendorDetails" rows="5" readonly></textarea>
                      </div>                    
                      <div class="col-sm-4">
                        <label for="addressDetails" class="form-label">Address Details</label>
                        <textarea class="form-control" id="addressDetails" rows="5" readonly></textarea>
                      </div>
                      <br><br><br>
                      
                      </div>
                    <div class="row mb-3">
                      <div class="col-sm-2">
                        <label for="gst" class="form-label">GST (%)</label>
                        <input type="number" class="form-control" id="gst" name="gst" value="18" oninput="calculateTotals()">
                      </div>
                    </div>  
                    </div>
        
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th scope="col">Sr. No</th>
                    <th scope="col">Item & Description</th>
                    <th scope="col">HSN/SAC</th>
                    <th scope="col">Qty</th>
                    <th scope="col">Rate (INR)</th>
                    <th scope="col">IGST</th>
                    <th scope="col">GST Amount (INR)</th>
                    <th scope="col">Amount (INR)</th>
                    <th scope="col">Action</th>
                  </tr>
                </thead>
                <tbody id="itemTable">
                  {% for item in items %}
                    {% for i in item%}
                  <tr>
                    <td class="content-cell">{{loop.index}}</td>
                    <td class="content-cell"><input type="text" class="form-control" name="description[]" value="{{ i['item_code'] }}"></td>
                    <td class="content-cell"><input type="text" class="form-control" name="hsn[]"></td>
                    <td class="content-cell"><input type="number" class="form-control qty" name="qty[]" oninput="calculateAmount(this)"></td>
                    <td class="content-cell"><input type="number" class="form-control rate" name="rate[]" oninput="calculateAmount(this)"></td>
                    <td class="content-cell"><span class="igst">18%</span></td>
                    <td class="content-cell"><input type="number" class="form-control gst-amount" name="gstAmount[]" readonly></td>
                    <td class="content-cell"><input type="number" class="form-control amount" name="amount[]" readonly></td>
                    <td><button type="button" class="btn btn-danger btn-sm" onclick="removeItemRow(this)">Remove</button></td>
                  </tr>
                  {% endfor %}
                  {% endfor %}
                </tbody>
              </table>
              <button type="button" class="btn btn-primary" onclick="addItem()">Add Item</button>
              <button type="submit" class="btn btn-success">Submit</button>
              <div class="row mt-4">
                <div class="col-sm-8">
                  <p><strong>Amount (In Words):</strong> <span id="amountInWords">Zero Only</span></p>
                </div>
                <div class="col-sm-4">
                  <table class="table table-bordered">
                    <tbody>
                      <tr>
                        <td>Sub-Total:</td>
                        <td id="subTotal">0</td>
                      </tr>
                      <tr>
                        <td>IGST:</td>
                        <td id="igstAmount">0</td>
                      </tr>
                      <tr>
                        <td><strong>Grand Total:</strong></td>
                        <td id="grandTotal">0</td>
                        <input type="hidden" name="grand_total" id="grand_total">
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-sm-3">
                    <label for="status" class="form-label">Director Approval</label>
                    {% if user_role in ['superadmin'] %}
                        <select class="form-select" id="status" name="status">
                            <option value="">Select Approval Status</option>
                            <option value="Approved">Approved</option>
                            <option value="Rejected">Rejected</option>
                            <option value="Pending">Pending</option>
                        </select>
                    {% else %}
                        <input type="text" class="form-control" id="status" name="status" value="Pending" readonly>
                    {% endif %}
                </div>
            </div>
              <div style="padding-left: 15px;">
              <div class="row mb-3">
                <button type="submit" class="btn btn-success" onclick="SubmitEvent">Submit</button>
              </div>
              </div>
            </form>
          </div>            
        </div>
    </div>
 
</body>
</html>

then there is poindex.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='add_item_style.css') }}">
  
</head>
<body>

    <div class="header">
        <h4>PARAS ANTI-DRONE TECHNOLOGIES PVT</h4>
    </div>

    <div class="mainbox">
        <div class="menubar">
            <a href="#">HOME</a>
            <a href="#">PURCHASE</a>
            <a href="#">PRODUCTION</a>
            <a href="#">PROJECTS</a>
        </div>
        <div class="content">
            <div class="container-fluid mt-5">
                <h1 class="text-center mb-4">Purchase Order List for Indent {{ indent_number }}</h1>
                <table class="table table-bordered table-hover">
                    <thead class="thead-dark">
                        <tr>
                            <th>Sr. No</th>
                            <th>PO Number</th>
                            <th>Approval Status</th>
                            <th>Action</th>
                            <th>Download</th>
                            <th>PA</th>
                            <th>GRN</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i, po in enumerate(purchase_orders) %}
                        <tr>
                            <td>{{ i + 1 }}</td>
                            <td>
                                <a href="{{ url_for('purchaseorder', indent_number=indent_number) }}" class="po-number-link">
                                    {{ po['po_number'] }}
                                </a>
                            </td>
                            <td>{{ po['approval_status'] }}</td>
                            <td>
                                <form action="{{ url_for('delete_po') }}" method="POST" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <input type="hidden" name="indent_number" value="{{ indent_number }}">
                                    <button type="submit" class="btn btn-danger btn-sm"   {% if user_role in ['team_leader_user', 'procurement_user', 'store_user', 'account_user'] %}disabled{% endif %}
                                            >
                                        Delete
                                    </button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('download_po') }}" method="POST" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-primary btn-sm">Download</button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('paindex', po_number=po['po_number']) }}" method="GET" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-warning btn-sm"  {% if user_role in ['team_leader_user', 'store_user',] %}disabled{% endif %}>PA</button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('grnindex', po_number=po['po_number']) }}" method="GET" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-info btn-sm"  {% if user_role in ['team_leader_user', 'procurement_user', 'account_user'] %}disabled{% endif %}>GRN</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="text-center mt-3">
                    <a href="{{ url_for('purchaseorder', indent_number=indent_number | urlencode) }}" class="btn btn-success">Create New PO</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
this is po route then purchaseorder.html and poindex i want same functionality like indent po no clickable and show then same form with prefilled details of that po 

ChatGPT said:
ChatGPT

3/3

You said:
Po Route in flask application

CSV_FILE = 'purchase_orders.csv'

def generate_po_number():
    """Generate a new PO number based on the number of existing entries in the CSV."""
    with open(CSV_FILE, 'r') as file:
        lines = file.readlines()
        return f'PADT/23-24/{len(lines) + 1:04d}'

def get_po_by_number(po_number):
    with open(CSV_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        items = []
        for row in reader:
            if row and row[0] == po_number:  # Ensure the row is not empty and PO number is at index 0
                for i in range(8, len(row), 7):
                    if i + 6 < len(row):  # Ensure there are enough columns for items
                        items.append({
                            'description': row[i],
                            'hsn': row[i + 1],
                            'quantity': row[i + 2],
                            'rate': row[i + 3],
                            'gstAmount': row[i + 4],
                            'amount': row[i + 5]
                        })
        if items:  # Check if items list is not empty
            return {
                'po_number': row[0],
                'indent': row[1],
                'po_date': row[2],
                'delivery_date': row[3],
                'gst': row[4],
                'status': row[5],
                'vendor': row[6],
                'bill_ship_to': row[7],
                'items': items,
                'grand_total': row[-1]
            }
    return None

@app.route('/purchaseorder/<path:indent_number>/', methods=['GET', 'POST'])
def purchaseorder(indent_number):
    decoded_indent_number = unquote(indent_number)
    
    if request.method == 'POST':
        # Extract form data
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
        amount_in_words = num2words(grand_total, to='currency', lang='en_IND')
        
        
        # Save data to CSV file
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            for i in range(len(descriptions)):
                writer.writerow([
                    po_number, decoded_indent_number, po_date, delivery_date, gst, status, vendor, 
                    billShipToId, descriptions[i], hsns[i], quantities[i], rates[i], gstAmounts[i], 
                    amounts[i], grand_total
                ])
        
        return redirect(url_for('poindex', indent_number=indent_number))
    
    # Render the purchase order form template
    items = []  # You need to adjust this based on your data structure
    # For example, if indents is a list of dictionaries, adjust accordingly
    for t in indents:
        if indent_number == t['indent_number']:
            items.append(t['items'])
    
    
    user_role = session.get('role')  # Get the user's role from the session
    return render_template('purchaseorder.html', indent_number=decoded_indent_number, items=items, user_role=user_role)

def get_vendor_by_display_name(display_name):
    vendors = load_vendors()
    for vendor in vendors:
        if vendor['vendor_display_name'] == display_name:
            return vendor
    return None

@app.route('/download_po', methods=['POST'])
def download_po():
    po_number = request.form.get('po_number')
    po = get_po_by_number(po_number)  # Assuming this function fetches the PO details
    
    if po:
        # Fetch address details
        address_id = po.get('bill_ship_to')  # Assuming 'bill_ship_to' is the address ID
        addresses = {
            1: 'Paras Antidrone Technologies (Nerul)\nD-112, 1st Floor, TTC Industrial Area, Nerul MIDC, Nerul, Maharashtra,\n400706, India\nGSTIN: 27AAKCP3967C1Z7\nPhone: 02227629910, Fax: 02227629910\nEmail ID: info@parasantidrone.com',
            2: 'Paras Antidrone Technologies (Bengaluru)\n23, 2nd Floor, Sankey Square, Sankey Road, Lower Palace Orchards, Bengaluru - 560003\nGSTIN: 27AAKCP3967C1Z7\nTel: 080-23464139/4142, Fax: 02227629910\nEmail ID: info@parasantidrone.com'
        }
        address_details = addresses.get(int(address_id), '') if address_id else ''
        
        # Fetch vendor details
        vendor_display_name = po.get('vendor')
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
        total = sum(float(item['amount']) for item in po['items'])
        gst_total = sum(float(item['gstAmount']) for item in po['items'])
        
        # Render and prepare response
        rendered = render_template('download_po.html',
                                   po_number=po['po_number'],
                                   po_date=po['po_date'],
                                   delivery_date=po['delivery_date'],
                                   gst=po['gst'],
                                   status=po['status'],
                                   vendor=vendor_details,  # Pass vendor details to template
                                   address_details=address_details,  # Pass address details to template
                                   items=po['items'],
                                   amount=total,
                                   gstitem=gst_total,
                                   grandtotal=po['grand_total'])
        
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

then below is purchaseorder.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='add_item_style.css') }}">
    <style>
        /* Reset default styles */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }

        .header {
            background-color: #004080;
            color: white;
            text-align: center;
            padding: 35px 0;
            font-size: 24px;
            border-bottom: 3px solid #003366;
        }
        .mainbox {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .menubar {
            background-color: #0059b3;
            color: white;
            padding: 20px;
            border-right: 3px solid #003366;
            flex-shrink: 0; /* menubar won't shrink */
        }

        .menubar a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            transition: background-color 0.3s, color 0.3s;
            font-size: 16px;
        }

        .menubar a:hover {
            background-color: #003366;
            color: #e6e6e6;
        }

        .content {
            flex-grow: 1;
            padding: 30px;
            background: radial-gradient(circle, #e6f2ff, #cce0ff, #99ccff, #6699ff);
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin: 20px;
        }



        .content h1 {
            color: #004080;
        }

        /* Responsive layout */
        @media (min-width: 768px) {
            .mainbox {
                flex-direction: row;
            }

            .content {
                margin: 20px;
            }
        }
    </style>
</head>
<body>

    <div class="header">
        <h4>PARAS ANTI-DRONE TECHNOLOGIES PVT</h4>
    </div>

    <div class="mainbox">
        <div class="menubar">
            <a href="#">HOME</a>
            <a href="#">PURCHASE</a>
            <a href="#">PRODUCTION</a>
            <a href="#">PROJECTS</a>
        </div>
        <div class="content">
          <div class="container-fluid mt-5">
            <h2 class="text-center my-4">PO Form for Indent {{ indent_number }}</h2>
            <form action="{{ url_for('purchaseorder', indent_number=indent_number, items=items) }}" method="post">
              <div class="mb-3">
                <label for="po_number" class="form-label">PO Number</label>
                <input type="text" class="form-control" id="po_number" name="po_number" value="PADT/23-24/0001" readonly>
              </div>
              <div class="mb-3">
                <label for="po_date" class="form-label">PO Date</label>
                <input type="date" class="form-control" id="po_date" name="po_date" required>
              </div>
              <div class="mb-3">
                <label for="delivery_date" class="form-label">Delivery Date</label>
                <input type="date" class="form-control" id="delivery_date" name="delivery_date" required>
              </div>
              <!-- Add a hidden input field for indent_number -->
              <div class="row mb-3">
                <div class="col-sm-4">
                  <label for="vendor" class="form-label">Select Vendor</label>
                  <br>
                  <select class="form-select" id="vendor" name="vendor">
                    <option value="">Select Vendor</option>
                  </select>
                </div>
                <div style="padding-left: 80px;">
                <div class="col-sm-4">
                  <label for="billShipTo" class="form-label">Select Address</label>
                  <select class="form-select" id="billShipTo" name="billShipTo">
                    <option value="">Select Address</option>
                  </select>
                </div>
                </div>
              </div>
                    <div class="row mb-3">
                      <div class="col-sm-5">
                        <label for="vendorDetails" class="form-label">Vendor Details</label>
                        <textarea class="form-control" id="vendorDetails" rows="5" readonly></textarea>
                      </div>                    
                      <div class="col-sm-4">
                        <label for="addressDetails" class="form-label">Address Details</label>
                        <textarea class="form-control" id="addressDetails" rows="5" readonly></textarea>
                      </div>
                      <br><br><br>
                      </div>
                    <div class="row mb-3">
                      <div class="col-sm-2">
                        <label for="gst" class="form-label">GST (%)</label>
                        <input type="number" class="form-control" id="gst" name="gst" value="18" oninput="calculateTotals()">
                      </div>
                    </div>  
                    </div>
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th scope="col">Sr. No</th>
                    <th scope="col">Item & Description</th>
                    <th scope="col">HSN/SAC</th>
                    <th scope="col">Qty</th>
                    <th scope="col">Rate (INR)</th>
                    <th scope="col">IGST</th>
                    <th scope="col">GST Amount (INR)</th>
                    <th scope="col">Amount (INR)</th>
                    <th scope="col">Action</th>
                  </tr>
                </thead>
                <tbody id="itemTable">
                  {% for item in items %}
                    {% for i in item%}
                  <tr>
                    <td class="content-cell">{{loop.index}}</td>
                    <td class="content-cell"><input type="text" class="form-control" name="description[]" value="{{ i['item_code'] }}"></td>
                    <td class="content-cell"><input type="text" class="form-control" name="hsn[]"></td>
                    <td class="content-cell"><input type="number" class="form-control qty" name="qty[]" oninput="calculateAmount(this)"></td>
                    <td class="content-cell"><input type="number" class="form-control rate" name="rate[]" oninput="calculateAmount(this)"></td>
                    <td class="content-cell"><span class="igst">18%</span></td>
                    <td class="content-cell"><input type="number" class="form-control gst-amount" name="gstAmount[]" readonly></td>
                    <td class="content-cell"><input type="number" class="form-control amount" name="amount[]" readonly></td>
                    <td><button type="button" class="btn btn-danger btn-sm" onclick="removeItemRow(this)">Remove</button></td>
                  </tr>
                  {% endfor %}
                  {% endfor %}
                </tbody>
              </table>
              <button type="button" class="btn btn-primary" onclick="addItem()">Add Item</button>
              <button type="submit" class="btn btn-success">Submit</button>
              <div class="row mt-4">
                <div class="col-sm-8">
                  <p><strong>Amount (In Words):</strong> <span id="amountInWords">Zero Only</span></p>
                </div>
                <div class="col-sm-4">
                  <table class="table table-bordered">
                    <tbody>
                      <tr>
                        <td>Sub-Total:</td>
                        <td id="subTotal">0</td>
                      </tr>
                      <tr>
                        <td>IGST:</td>
                        <td id="igstAmount">0</td>
                      </tr>
                      <tr>
                        <td><strong>Grand Total:</strong></td>
                        <td id="grandTotal">0</td>
                        <input type="hidden" name="grand_total" id="grand_total">
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-sm-3">
                    <label for="status" class="form-label">Director Approval</label>
                    {% if user_role in ['superadmin'] %}
                        <select class="form-select" id="status" name="status">
                            <option value="">Select Approval Status</option>
                            <option value="Approved">Approved</option>
                            <option value="Rejected">Rejected</option>
                            <option value="Pending">Pending</option>
                        </select>
                    {% else %}
                        <input type="text" class="form-control" id="status" name="status" value="Pending" readonly>
                    {% endif %}
                </div>
            </div>
              <div style="padding-left: 15px;">
              <div class="row mb-3">
                <button type="submit" class="btn btn-success" onclick="SubmitEvent">Submit</button>
              </div>
              </div>
            </form>
          </div>            
        </div>
    </div>
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        // Fetch vendors from CSV file and populate dropdown
        fetch('/get_vendors') // Replace with your Flask route to fetch vendors
          .then(response => response.json())
          .then(data => {
            const vendorSelect = document.getElementById('vendor');
            data.forEach(vendor => {
              const option = document.createElement('option');
              option.value = vendor.vendor_display_name; // Adjust as per your vendor data structure
              option.textContent = vendor.vendor_display_name;
              vendorSelect.appendChild(option);
            });
          })
          .catch(error => console.error('Error fetching vendors:', error));
      });
      function addItem() {
        const table = document.getElementById('itemTable');
        const rowCount = table.rows.length + 1;
        const row = table.insertRow();
        row.innerHTML = 
          <td class="content-cell">${rowCount}</td>
          <td class="content-cell"><input type="text" class="form-control" name="description[]"></td>
          <td class="content-cell"><input type="text" class="form-control" name="hsn[]"></td>
          <td class="content-cell"><input type="number" class="form-control qty" name="qty[]" oninput="calculateAmount(this)"></td>
          <td class="content-cell"><input type="number" class="form-control rate" name="rate[]" oninput="calculateAmount(this)"></td>
          <td class="content-cell"><span class="igst">${document.getElementById('gst').value}%</span></td>
          <td class="content-cell"><input type="number" class="form-control gst-amount" name="gstAmount[]" readonly></td>
          <td class="content-cell"><input type="number" class="form-control amount" name="amount[]" readonly></td>
          <td><button type="button" class="btn btn-danger btn-sm" onclick="removeItemRow(this)">Remove</button></td>
        ;
      }
  
      function calculateAmount(element) {
        const row = element.closest('tr');
        const qty = row.querySelector('.qty').value;
        const rate = row.querySelector('.rate').value;
        const amount = qty * rate;
        const gst = parseFloat(document.getElementById('gst').value) || 0;
        const gstAmount = (amount * gst) / 100;
        row.querySelector('.gst-amount').value = gstAmount.toFixed(2);
        row.querySelector('.amount').value = amount.toFixed(2);
        calculateTotals();
      }
  
      function calculateTotals() {
        let subTotal = 0;
        let gstTotal = 0;
        const gst = parseFloat(document.getElementById('gst').value) || 0;
  
        document.querySelectorAll('.amount').forEach(input => {
          subTotal += parseFloat(input.value) || 0;
        });
  
        document.querySelectorAll('.gst-amount').forEach(input => {
          gstTotal += parseFloat(input.value) || 0;
        });
  
        const grandTotal = subTotal + gstTotal;
  
        document.getElementById('subTotal').textContent = subTotal.toFixed(2);
        document.getElementById('igstAmount').textContent = gstTotal.toFixed(2);
        document.getElementById('grandTotal').textContent = grandTotal.toFixed(2);
        document.getElementById('amountInWords').textContent = numberToWords(grandTotal) + ' Only';
  
        document.getElementById('grand_total').value = grandTotal.toFixed(2);
  
        document.querySelectorAll('.igst').forEach(span => {
          span.textContent = ${gst}%;
        });
      }
  
      function removeItemRow(button) {
              var row = button.parentNode.parentNode;
              row.parentNode.removeChild(row);
              rowCount--;
              updateRowNumbers();}
  
      function numberToWords(number) {
        const units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
        const teens = ['Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
        const tens = ['', 'Ten', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
        const scales = ['', 'Thousand', 'Million', 'Billion', 'Trillion'];
  
        if (number === 0) return 'Zero';
  
        let words = [];
        let chunkIndex = 0;
  
        // Separate integer and fractional parts
        let [integerPart, decimalPart] = number.toFixed(2).toString().split('.');
        integerPart = parseInt(integerPart, 10);
  
        // Process integer part
        while (integerPart > 0) {
          let chunk = integerPart % 1000;
          integerPart = Math.floor(integerPart / 1000);
  
          if (chunk !== 0) {
            let chunkWords = [];
  
            if (chunk >= 100) {
              chunkWords.push(units[Math.floor(chunk / 100)] + ' Hundred');
              chunk %= 100;
            }
  
            if (chunk >= 11 && chunk <= 19) {
              chunkWords.push(teens[chunk - 11]);
            } else if (chunk >= 20 || chunk === 10) {
              chunkWords.push(tens[Math.floor(chunk / 10)]);
              chunk %= 10;
            }
  
            if (chunk > 0 && chunk < 10) {
              chunkWords.push(units[chunk]);
            }
  
            if (chunkWords.length > 0) {
              if (chunkIndex > 0) {
                chunkWords.push(scales[chunkIndex]);
              }
              words.unshift(chunkWords.join(' '));
            }
          }
  
          chunkIndex++;
        }
  
        // Process decimal part
        if (decimalPart && parseInt(decimalPart, 10) > 0) {
          words.push('and ' + (decimalPart.length === 1 ? decimalPart + '0' : decimalPart) + ' Paise');
        }
  
        return words.join(' ');
      }
  
  
      document.addEventListener('DOMContentLoaded', function() {
        // Fetch vendors from Flask route '/get_vendors'
        fetch('/get_vendors')
          .then(response => response.json())
          .then(data => {
            const vendorSelect = document.getElementById('vendor');
            data.forEach(vendor => {
              const option = document.createElement('option');
              option.value = vendor.vendor_display_name; // Adjust as per your vendor data structure
              option.textContent = vendor.vendor_display_name;
              vendorSelect.appendChild(option);
            });
          })
          .catch(error => console.error('Error fetching vendors:', error));
      });
      
      // Function to handle vendor selection and display details
      document.getElementById('vendor').addEventListener('change', function() {
        const selectedVendor = this.value;
        fetch('/get_vendors')
          .then(response => response.json())
          .then(data => {
            const selectedVendorData = data.find(vendor => vendor.vendor_display_name === selectedVendor);
            if (selectedVendorData) {
              const vendorDetailsTextarea = document.getElementById('vendorDetails');
              vendorDetailsTextarea.value = Company: ${selectedVendorData.company_name}\n;
              vendorDetailsTextarea.value += Contact Person: ${selectedVendorData.contact_persons}\n;
              vendorDetailsTextarea.value += Address: ${selectedVendorData.address}\n;
              vendorDetailsTextarea.value += Email: ${selectedVendorData.vendor_email}\n;
              vendorDetailsTextarea.value += GSTIN: ${selectedVendorData.gst_treatment}\n;
              // Add more fields as needed
            }
          })
          .catch(error => console.error('Error fetching vendors:', error));
      });
      document.addEventListener('DOMContentLoaded', function() {
        fetch('/get_addresses')
          .then(response => response.json())
          .then(data => {
            const billShipToSelect = document.getElementById('billShipTo');
            data.forEach(address => {
              const option = document.createElement('option');
              option.value = address.id;
              option.textContent = address.display_name;
              billShipToSelect.appendChild(option);
            });
    
            billShipToSelect.addEventListener('change', function() {
              const selectedAddress = data.find(address => address.id == this.value);
              document.getElementById('addressDetails').value = selectedAddress ? selectedAddress.details : '';
            });
          })
          .catch(error => console.error('Error fetching addresses:', error));
      });
      
    </script>
</body>
</html>

then there is poindex.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='add_item_style.css') }}">

</head>
<body>
    <div class="header">
        <h4>PARAS ANTI-DRONE TECHNOLOGIES PVT</h4>
    </div>

    <div class="mainbox">
        <div class="menubar">
            <a href="#">HOME</a>
            <a href="#">PURCHASE</a>
            <a href="#">PRODUCTION</a>
            <a href="#">PROJECTS</a>
        </div>
        <div class="content">
            <div class="container-fluid mt-5">
                <h1 class="text-center mb-4">Purchase Order List for Indent {{ indent_number }}</h1>
                <table class="table table-bordered table-hover">
                    <thead class="thead-dark">
                        <tr>
                            <th>Sr. No</th>
                            <th>PO Number</th>
                            <th>Approval Status</th>
                            <th>Action</th>
                            <th>Download</th>
                            <th>PA</th>
                            <th>GRN</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i, po in enumerate(purchase_orders) %}
                        <tr>
                            <td>{{ i + 1 }}</td>
                            <td>
                                <a href="{{ url_for('purchaseorder', indent_number=indent_number) }}" class="po-number-link">
                                    {{ po['po_number'] }}
                                </a>
                            </td>
                            <td>{{ po['approval_status'] }}</td>
                            <td>
                                <form action="{{ url_for('delete_po') }}" method="POST" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <input type="hidden" name="indent_number" value="{{ indent_number }}">
                                    <button type="submit" class="btn btn-danger btn-sm"   {% if user_role in ['team_leader_user', 'procurement_user', 'store_user', 'account_user'] %}disabled{% endif %}
                                            >
                                        Delete
                                    </button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('download_po') }}" method="POST" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-primary btn-sm">Download</button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('paindex', po_number=po['po_number']) }}" method="GET" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-warning btn-sm"  {% if user_role in ['team_leader_user', 'store_user',] %}disabled{% endif %}>PA</button>
                                </form>
                            </td>
                            <td>
                                <form action="{{ url_for('grnindex', po_number=po['po_number']) }}" method="GET" style="display:inline;">
                                    <input type="hidden" name="po_number" value="{{ po['po_number'] }}">
                                    <button type="submit" class="btn btn-info btn-sm"  {% if user_role in ['team_leader_user', 'procurement_user', 'account_user'] %}disabled{% endif %}>GRN</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="text-center mt-3">
                    <a href="{{ url_for('purchaseorder', indent_number=indent_number | urlencode) }}" class="btn btn-success">Create New PO</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>


