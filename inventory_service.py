from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import os
from database import get_session
from models import Product

app = Flask(__name__)

@app.route('/')
def home():
    return 'Inventory Service is running'

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    try:
        xml_data   = request.data
        root       = ET.fromstring(xml_data)
        product_id = root.find('ProductID').text
        quantity   = int(root.find('Quantity').text)

        session = get_session()
        product = session.query(Product).filter_by(product_id=product_id).first()

        response = ET.Element('InventoryResponse')

        if not product:
            ET.SubElement(response, 'Status').text  = 'Failed'
            ET.SubElement(response, 'Message').text = 'Product not found'
        elif product.stock < quantity:
            ET.SubElement(response, 'Status').text  = 'Failed'
            ET.SubElement(response, 'Message').text = 'Not enough stock'
        else:
            product.stock -= quantity
            session.commit()
            ET.SubElement(response, 'Status').text         = 'Success'
            ET.SubElement(response, 'Message').text        = 'Inventory updated'
            ET.SubElement(response, 'RemainingStock').text = str(product.stock)

        session.close()
        return Response(ET.tostring(response), mimetype='application/xml')

    except Exception as e:
        error = ET.Element('InventoryResponse')
        ET.SubElement(error, 'Status').text  = 'Failed'
        ET.SubElement(error, 'Message').text = str(e)
        return Response(ET.tostring(error), mimetype='application/xml')

@app.route('/check_stock/<product_id>', methods=['GET'])
def check_stock(product_id):
    try:
        session = get_session()
        product = session.query(Product).filter_by(product_id=product_id).first()
        session.close()
        if product:
            return f'Product {product_id} - {product.name} - Stock: {product.stock}'
        return f'Product {product_id} not found'
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)