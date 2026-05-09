from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import requests
import os
from database import get_session
from models import Order, Payment, Product

app = Flask(__name__)

INVENTORY_URL = os.getenv('INVENTORY_URL', 'http://localhost:5001/update_inventory')
PAYMENT_URL   = os.getenv('PAYMENT_URL',   'http://localhost:5002/process_payment')

@app.route('/health')
def health():
    return 'OK'

@app.route('/')
def home():
    return 'Order Service is running'

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        xml_data     = request.data
        root         = ET.fromstring(xml_data)
        product_id   = root.find('ProductID').text
        quantity     = int(root.find('Quantity').text)
        total_amount = quantity * 25

        # Step 1: call inventory service
        inv_resp = requests.post(
            INVENTORY_URL,
            data=xml_data,
            headers={'Content-Type': 'application/xml'},
            timeout=60
        )

        # Safe parse inventory response
        try:
            inv_root = ET.fromstring(inv_resp.content)
        except ET.ParseError:
            return Response(
                b'<Error>Inventory service returned invalid response. Wake it up first at https://lirhea-inventory.onrender.com then try again.</Error>',
                mimetype='application/xml'
            )

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

        pay_resp = requests.post(
            PAYMENT_URL,
            data=ET.tostring(payment_xml),
            headers={'Content-Type': 'application/xml'},
            timeout=60
        )

        # Safe parse payment response
        try:
            pay_root = ET.fromstring(pay_resp.content)
        except ET.ParseError:
            return Response(
                b'<Error>Payment service returned invalid response. Wake it up first at https://lirhea-payment.onrender.com then try again.</Error>',
                mimetype='application/xml'
            )

        # Step 3: save to database
        session = get_session()
        new_order = Order(
            product_id = product_id,
            quantity   = quantity,
            total      = total_amount,
            status     = 'Success'
        )
        session.add(new_order)
        session.commit()

        new_payment = Payment(
            order_id = new_order.id,
            amount   = total_amount,
            status   = pay_root.find('Status').text
        )
        session.add(new_payment)
        session.commit()
        session.close()

        return Response(pay_resp.content, mimetype='application/xml')

    except Exception as e:
        return Response(
            f'<Error>{str(e)}</Error>',
            mimetype='application/xml'
        )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)