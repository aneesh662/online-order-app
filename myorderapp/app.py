from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Products list
products = [
    {"id": 1, "name": "Burger", "price": 10},
    {"id": 2, "name": "Pizza", "price": 20},
    {"id": 3, "name": "Pasta", "price": 15},
    {"id": 4, "name": "Salad", "price": 8}
]

EXCEL_FILE = "orders.xlsx"

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Customer Name", "Address", "Contact", "Email", "Item", "Quantity", "Total Price"])
    df.to_excel(EXCEL_FILE, index=False)


def send_email(to_email, subject, body):
    sender_email = "kodiyattilaneesh@gmail.com"  # Replace with your email
    sender_password = "Akm@2541662"  # Use app password if Gmail

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully to", to_email)
    except Exception as e:
        print("Error sending email:", e)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        address = request.form["address"]
        contact = request.form["contact"]
        email = request.form["email"]
        item_id = int(request.form["item"])
        quantity = int(request.form["quantity"])

        product = next(p for p in products if p["id"] == item_id)
        total_price = product["price"] * quantity

        # Save to Excel
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([{
            "Customer Name": customer_name,
            "Address": address,
            "Contact": contact,
            "Email": email,
            "Item": product["name"],
            "Quantity": quantity,
            "Total Price": total_price
        }])])
        df.to_excel(EXCEL_FILE, index=False)

        # Send confirmation email
        subject = "Order Confirmation"
        body = f"Dear {customer_name},\n\n" \
               f"Thank you for ordering {quantity} {product['name']}(s).\n" \
               f"We will deliver to: {address}.\n" \
               f"Total amount: AED {total_price}.\n\n" \
               f"Regards,\nYour Restaurant"
        send_email(email, subject, body)

        return redirect(url_for("index"))

    return render_template("index.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)
