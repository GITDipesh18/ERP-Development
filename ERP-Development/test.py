def generate_po_number():
    """Generate a new PO number based on the highest existing PO number in the CSV."""
    highest_po_number = 0
    
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists
            
            for row in reader:
                if not row:  # Skip empty rows
                    continue
                
                try:
                    po_number = row[0]  # Assuming PO number is in the first column
                    # Extract the numeric part of the PO number
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
        # po_url = url_for('purchaseorder', indent_number=decoded_indent_number, po_number=po_number, _external=True)
        
        # # Send email
        # msg = Message('New Purchase Order Created', sender='shelardipesh18@gmail.com', recipients=['shelardipesh18@gmail.com'])
        
        # msg.body = f"""
        # PO Number: {po_number}
        # Indent Number: {decoded_indent_number} 
        
        # Direct PO Link: {po_url}
        # Server Link: http://127.0.0.1:5000/
        # """
        # mail.send(msg)

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
