from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)


@app.route("/")
def home():
    return "Payment Service is running"


@app.route("/process_payment", methods=["POST"])
def process_payment():
    try:
        xml_data = request.data
        root = ET.fromstring(xml_data)

        amount = float(root.find("Amount").text)

        response = ET.Element("PaymentResponse")

        # Simple validation logic (you can improve later)
        if amount <= 0:
            ET.SubElement(response, "Status").text = "Failed"
            ET.SubElement(response, "Message").text = "Invalid amount"
        else:
            ET.SubElement(response, "Status").text = "Success"
            ET.SubElement(response, "Message").text = "Payment processed"

        return Response(
            ET.tostring(response),
            mimetype="application/xml"
        )

    except Exception as e:
        error = ET.Element("PaymentResponse")
        ET.SubElement(error, "Status").text = "Failed"
        ET.SubElement(error, "Message").text = str(e)

        return Response(
            ET.tostring(error),
            mimetype="application/xml"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)