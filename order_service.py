from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import requests
from database import get_session
from models import Order, Payment

app = Flask(__name__)

INVENTORY_URL = 'https://lirhea-inventory.onrender.com/update_inventory'
PAYMENT_URL   = 'https://lirhea-payment.onrender.com/process_payment'

@app.route('/place_order', methods=['POST'])
def place_order():
    xml_data     = request.data
    root         = ET.fromstring(xml_data)
    product_id   = root.find('ProductID').text
    quantity     = int(root.find('Quantity').text)
    total_amount = quantity * 25

    # Save order request to XML file
    ET.ElementTree(ET.fromstring(xml_data)).write('order_request.xml')

    # Step 1: call inventory service
    inv_resp = requests.post(INVENTORY_URL, data=xml_data,
                             headers={'Content-Type': 'application/xml'})
    inv_root = ET.fromstring(inv_resp.content)
    ET.ElementTree(inv_root).write('inventory_response.xml')

    if inv_root.find('Status').text != 'Success':
        # Save failed order to database
        session = get_session()
        session.add(Order(
            product_id = product_id,
            quantity   = quantity,
            total      = total_amount,
            status     = 'Failed'
        ))
        session.commit()
        session.close()
        return Response(inv_resp.content, mimetype='application/xml')

    # Step 2: call payment service
    payment_xml = ET.Element('Payment')
    ET.SubElement(payment_xml, 'Amount').text = str(total_amount)
    pay_resp = requests.post(PAYMENT_URL, data=ET.tostring(payment_xml),
                             headers={'Content-Type': 'application/xml'})

    # Check if payment service returned valid XML
    if not pay_resp.content:
        return Response(b'<PaymentResponse><Status>Failed</Status><Message>Payment service error</Message></PaymentResponse>',
                        mimetype='application/xml')

    pay_root = ET.fromstring(pay_resp.content)
    ET.ElementTree(pay_root).write('payment_response.xml')

    # Save order to database first to get the order ID
    session = get_session()
    new_order = Order(
        product_id = product_id,
        quantity   = quantity,
        total      = total_amount,
        status     = 'Success'
    )
    session.add(new_order)
    session.commit()

    # Save payment using the real order ID
    new_payment = Payment(
        order_id = new_order.id,
        amount   = total_amount,
        status   = pay_root.find('Status').text
    )
    session.add(new_payment)
    session.commit()
    session.close()

    return Response(pay_resp.content, mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5000)