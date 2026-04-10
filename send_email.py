"""
send_email.py
-------------
Sends an email with a randomly generated body and a random image attachment
picked from the ./images directory via Gmail SMTP (SSL on port 465).

Requirements:
    pip install python-dotenv

Usage:
    1. Create a .env file in the same directory:
         EMAIL_SENDER=you@gmail.com
         EMAIL_PASSWORD=your_app_password
         EMAIL_RECEIVER=recipient@example.com

    2. Place images inside the ./images directory (jpg, jpeg, png, gif, webp)

    3. python send_email.py
"""

import os
import random
import string
import smtplib
import mimetypes
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv


# ── Configuration ─────────────────────────────────────────────────────────────

load_dotenv()

SENDER   = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("EMAIL_RECEIVER")

if not all([SENDER, PASSWORD, RECEIVER]):
    missing = [k for k, v in {"EMAIL_SENDER": SENDER, "EMAIL_PASSWORD": PASSWORD, "EMAIL_RECEIVER": RECEIVER}.items() if not v]
    raise EnvironmentError(f"Missing required variables in .env: {', '.join(missing)}")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465          # SSL


# ── Random body generator ─────────────────────────────────────────────────────

SUBJECTS = [
    "Salary Disbursement Request - Acme Innovations Inc",
    "Salary Disbursement - Golden Dragon Trading Ltd",
    "Salary Disbursement - Apex Trading Ltd",
    "Salary Disbursement - Omni Corp",
    "Salary Disbursement - Blue Sun Corp",
]

OPENERS = [
    "Hope you're having a great day!",
    "Just wanted to reach out.",
    "Dropping you a quick note.",
    "This email was generated automatically.",
    "Greetings from your Python script!",
]

BODIES = [
    """
        Dear Wave Money Operations Team,
    
        Please process the salary disbursement for Acme Innovations Inc.
        
        Amount: 25,000,000 MMK (SalaryToMA)
        Payroll Period: February 1-15, 2024
        Number of employees: 35
        
        The bank slip confirmation is attached for your verification.
        
        Approved by:
        - U Kyaw Zin, Sales HOD — Approved
        - Daw Su Su Lwin, Finance Manager — Approved
        
        Please confirm receipt and processing timeline.
        
        Best regards,
        Maria Chen
        Acme Innovations Inc.
    """,
    """
        Dear Wave Money Operations Team,

        Please process monthly salary disbursement for Golden Dragon Trading Ltd.
        
        Amount: 15,000,000 MMK (SalaryToMA)
        Payment Period: March 2024
        Total employees: 22
        
        Approved by:
        - U Aung Myint, Sales HOD — Approved
        - Daw Aye Myint, Finance Manager — Approved
        
        Employee list and bank slip will follow separately.
        
    """,
    """
        Dear Team,

        We are pleased to inform you that the salary disbursement for the period of April 2026 has been successfully processed via SalaryToMA.
        
        The funds have been transferred from the Corporate Wallet to your respective accounts. You should see the credit reflected in your balance shortly.
        
        Disbursement Details:
        
        Company: [Company Name] Ltd
        
        Payment Type: SalaryToMA (Direct Wallet Transfer)
        
        Period: April 1 – April 30, 2026
        
        Currency: MMK
        
        Please find your individual pay slips attached to this email for your records. We kindly ask you to review the details and ensure that the credited amount aligns with your statement.
        
        If you notice any discrepancies or have questions regarding your disbursement, please reply to this email or contact the HR/Finance department at [Phone Number/Extension].
        
        Thank you for your hard work and continued dedication to the team.
        
    """,
    """
        Dear Employees,

        This email is to confirm that your salary for the month of April 2026 has been disbursed today via the SalaryToMA system.
        
        Payment Summary
        Disbursement Method: Corporate Wallet to Employee Wallet
        
        Status: Processed
        
        Transaction Date: April 10, 2026
        
        Company: [Company Name] Ltd
        
        Paystub Access:
        Your detailed digital payslip, including breakdowns of base salary, bonuses, and deductions, is now available for download through the employee portal.
        
        Note: Depending on your mobile provider or wallet sync timing, it may take a few moments for the notification to appear on your device.
        
        If you have any questions regarding your payroll or do not receive your funds within 24 hours, please reach out to the Finance Team at finance@[companyname].com.
        
        Thank you for your valuable contributions this month.
        
    """,
    """
        Hi Team,
        
        It’s that time of the month! We’ve just hit "send" on the salary disbursement for April 2026 using the SalaryToMA platform.
        
        What you need to know:
        
        Method: Direct transfer to your mobile wallet.
        
        Timing: You should receive a text notification within the hour.
        
        Company: [Company Name] Ltd
        
        We’ve attached your individual salary breakdown (PDF) to this email. Please take a quick look to make sure everything looks right.
        
        If you have any issues with your transfer or questions about the numbers, just give the Finance team a shout—we’re happy to help!
        
        Thanks for all the amazing work you’ve put in this month. Enjoy the weekend!
        
    """,
]

CLOSERS = [
    "Best regards",
    "Cheers",
    "Warm wishes",
    "Until next time",
    "Take care",
]


def random_body() -> tuple[str, str]:
    """Return (subject, body) with random content."""
    subject = random.choice(SUBJECTS)

    paragraphs = [
        random.choice(OPENERS),
        " ".join(random.choices(BODIES)),
        "Random token: " + "".join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        random.choice(CLOSERS) + ",\nPython Mailer",
    ]
    body = "\n\n".join(paragraphs)
    return subject, body


# ── Random image picker ───────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
IMAGES_DIR = Path("images")


def pick_random_image() -> Path:
    """Return a random image path from the ./images directory."""
    if not IMAGES_DIR.exists():
        raise FileNotFoundError(f"Images directory '{IMAGES_DIR}' not found.")

    images = [f for f in IMAGES_DIR.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]

    if not images:
        raise FileNotFoundError(f"No images found in '{IMAGES_DIR}' (supported: {IMAGE_EXTENSIONS}).")

    return random.choice(images)


# ── Email builder & sender ────────────────────────────────────────────────────

def build_message(sender: str, receiver: str) -> tuple[MIMEMultipart, str]:
    subject, body = random_body()
    image_path    = pick_random_image()

    msg = MIMEMultipart()
    msg["From"]    = sender
    msg["To"]      = receiver
    msg["Subject"] = subject

    # Plain-text body
    msg.attach(MIMEText(body, "plain"))

    # Image attachment — detect MIME type from file extension
    mime_type, _ = mimetypes.guess_type(image_path)
    main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)

    with open(image_path, "rb") as f:
        img_part = MIMEBase(main_type, sub_type)
        img_part.set_payload(f.read())

    encoders.encode_base64(img_part)
    img_part.add_header("Content-Disposition", "attachment", filename=image_path.name)
    msg.attach(img_part)

    return msg, subject, image_path.name


def send_email(sender: str, password: str, receiver: str) -> None:
    msg, subject, image_name = build_message(sender, receiver)

    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} …")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

    print(f"✅  Email sent successfully!")
    print(f"   Subject   : {subject}")
    print(f"   From      : {sender}")
    print(f"   To        : {receiver}")
    print(f"   Attachment: {image_name}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    send_email(SENDER, PASSWORD, RECEIVER)