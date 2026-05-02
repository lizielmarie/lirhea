from flask import Flask, request, Response
import xml.etree.ElementTree as ET
from database import get_session
from models import Product

app = Flask(__name__)

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    xml_data   = request.data
    root       = ET.fromstring(xml_data)
    product_id = root.find('ProductID').text
    quantity   = int(root.find('Quantity').text)

    # ORM: query the product from MySQL instead of a dictionary
    session = get_session()
    product = session.query(Product).filter_by(product_id=product_id).first()

    response = ET.Element('InventoryResponse')

    if product and product.stock >= quantity:
        # ORM: deduct stock and save to database
        product.stock -= quantity
        session.commit()

        ET.SubElement(response, 'Status').text         = 'Success'
        ET.SubElement(response, 'RemainingStock').text = str(product.stock)
    else:
        ET.SubElement(response, 'Status').text  = 'Failed'
        ET.SubElement(response, 'Message').text = 'Insufficient stock'

    session.close()

    # Save response to XML file
    tree = ET.ElementTree(response)
    tree.write('inventory_response.xml')

    return Response(ET.tostring(response), mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5001)