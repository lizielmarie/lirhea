from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import requests
import os

from database import get_session
from models import Order, Payment

app = Flask(__name__)

# IMPORTANT: Use Render URLs (update these after deploying services)
INVENTORY_URL = os.getenv("INVENTORY_URL")
PAYMENT_URL = os.getenv("PAYMENT_URL")


@app.route("/")
def home():
    return "Order Service is running"


@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        xml_data = request.data
        root = ET.fromstring(xml_data)

        product_id = root.find('ProductID').text
        quantity = int(root.find('Quantity').text)
        total_amount = quantity * 25

        # Step 1: Inventory Service
        inv_resp = requests.post(
            INVENTORY_URL,
            data=xml_data,
            headers={'Content-Type': 'application/xml'}
        )

        inv_root = ET.fromstring(inv_resp.content)

        if inv_root.find('Status').text != 'Success':
            session = get_session()
            session.add(Order(
                product_id=product_id,
                quantity=quantity,
                total=total_amount,
                status='Failed'
            ))
            session.commit()
            session.close()

            return Response(inv_resp.content, mimetype='application/xml')

        # Step 2: Payment Service
        payment_xml = ET.Element('Payment')
        ET.SubElement(payment_xml, 'Amount').text = str(total_amount)

        pay_resp = requests.post(
            PAYMENT_URL,
            data=ET.tostring(payment_xml),
            headers={'Content-Type': 'application/xml'}
        )

        if not pay_resp.content:
            return Response(
                b'<PaymentResponse><Status>Failed</Status><Message>Payment error</Message></PaymentResponse>',
                mimetype='application/xml'
            )

        pay_root = ET.fromstring(pay_resp.content)

        # Save to DB
        session = get_session()

        new_order = Order(
            product_id=product_id,
            quantity=quantity,
            total=total_amount,
            status='Success'
        )
        session.add(new_order)
        session.commit()

        new_payment = Payment(
            order_id=new_order.id,
            amount=total_amount,
            status=pay_root.find('Status').text
        )
        session.add(new_payment)
        session.commit()
        session.close()

        return Response(pay_resp.content, mimetype='application/xml')

    except Exception as e:
        return Response(
            f"<Error>{str(e)}</Error>",
            mimetype='application/xml'
        )


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)