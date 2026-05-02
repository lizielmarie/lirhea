from flask import Flask, request, Response
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# Simple in-memory inventory (you can later replace with DB)
inventory = {
    "1": 10,
    "2": 5,
    "3": 0
}


@app.route("/")
def home():
    return "Inventory Service is running"


@app.route("/update_inventory", methods=["POST"])
def update_inventory():
    try:
        xml_data = request.data
        root = ET.fromstring(xml_data)

        product_id = root.find("ProductID").text
        quantity = int(root.find("Quantity").text)

        response = ET.Element("InventoryResponse")

        if product_id not in inventory:
            ET.SubElement(response, "Status").text = "Failed"
            ET.SubElement(response, "Message").text = "Product not found"
        elif inventory[product_id] < quantity:
            ET.SubElement(response, "Status").text = "Failed"
            ET.SubElement(response, "Message").text = "Not enough stock"
        else:
            inventory[product_id] -= quantity
            ET.SubElement(response, "Status").text = "Success"
            ET.SubElement(response, "Message").text = "Inventory updated"

        return Response(
            ET.tostring(response),
            mimetype="application/xml"
        )

    except Exception as e:
        error = ET.Element("InventoryResponse")
        ET.SubElement(error, "Status").text = "Failed"
        ET.SubElement(error, "Message").text = str(e)

        return Response(
            ET.tostring(error),
            mimetype="application/xml"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)