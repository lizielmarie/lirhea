from flask import Flask, request, Response
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    xml_data = request.data
    root     = ET.fromstring(xml_data)
    amount   = float(root.find('Amount').text)

    response = ET.Element('PaymentResponse')

    if amount > 0:
        ET.SubElement(response, 'Status').text = 'Success'
    else:
        ET.SubElement(response, 'Status').text  = 'Failed'
        ET.SubElement(response, 'Message').text = 'Invalid amount'

    # Save to XML file
    ET.ElementTree(response).write('payment_response.xml')

    return Response(ET.tostring(response), mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5002)