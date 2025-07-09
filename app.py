from flask import Flask, request, jsonify
from flask_cors import CORS
import random, time, smtplib

app = Flask(__name__)
CORS(app)

otp_store = {}  # key: email, value: dict with otp and timestamp

# Utility to generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Dummy email sender (configure properly for real use)
def send_email(recipient_email, otp):
    print(f"Sending OTP {otp} to {recipient_email}")
    # In production, use smtplib or an API like SendGrid or Mailgun here.

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data['email']
    phone = data['phone']  # for future SMS use
    otp = generate_otp()
    otp_store[email] = { 'otp': otp, 'timestamp': time.time() }

    send_email(email, otp)
    return jsonify({ 'success': True, 'message': 'OTP sent' })

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data['email']
    entered_otp = data['otp']

    if email not in otp_store:
        return jsonify({ 'valid': False, 'message': 'No OTP sent' })

    stored = otp_store[email]
    if time.time() - stored['timestamp'] > 120:  # 2 minute expiry
        return jsonify({ 'valid': False, 'message': 'Time expired' })

    if entered_otp == stored['otp']:
        return jsonify({ 'valid': True, 'message': 'Login successful' })
    else:
        return jsonify({ 'valid': False, 'message': 'Incorrect OTP' })

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    email = data['email']
    phone = data['phone']
    otp = generate_otp()
    otp_store[email] = { 'otp': otp, 'timestamp': time.time() }
    send_email(email, otp)
    return jsonify({ 'success': True, 'message': 'OTP resent' })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
