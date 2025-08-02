from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Environment variables
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
COLOR_FROM_ENV = os.environ.get("APP_COLOR", "lime")
MY_NAME = os.environ.get("MY_NAME", "Bastine Johns")

# S3 Config
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_FILE = os.environ.get("S3_FILE")

# MySQL connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# Color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
SUPPORTED_COLORS = ",".join(color_codes.keys())
COLOR = random.choice(list(color_codes.keys()))

# Helper to get background image URL
def get_background_url():
    try:
        s3 = boto3.client('s3')
        logging.info(f"Fetching background image from s3://{S3_BUCKET}/{S3_FILE}")
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': S3_BUCKET, 'Key': S3_FILE},
            ExpiresIn=3600
        )
    except Exception as e:
        logging.error(f"Failed to generate S3 URL: {e}")
        return None

@app.route("/", methods=['GET', 'POST'])
def home():
    url = get_background_url()
    return render_template('addemp.html', color=color_codes[COLOR], background_url=url, name=MY_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    url = get_background_url()
    return render_template('about.html', color=color_codes[COLOR], background_url=url, name=MY_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    url = get_background_url()
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR], background_url=url)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    url = get_background_url()
    return render_template("getemp.html", color=color_codes[COLOR], background_url=url, name=MY_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            return "Employee not found", 404
    except Exception as e:
        logging.error(f"Error fetching employee: {e}")
        return "Error occurred", 500
    finally:
        cursor.close()

    url = get_background_url()
    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"],
                           location=output["location"], color=color_codes[COLOR],
                           background_url=url, name=MY_NAME)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        COLOR = args.color
        logging.info(f"Color from command line argument = {COLOR}")
        if COLOR_FROM_ENV:
            logging.info(f"Environment color overridden by CLI: {COLOR_FROM_ENV}")
    elif COLOR_FROM_ENV:
        COLOR = COLOR_FROM_ENV
        logging.info(f"Color from environment variable = {COLOR}")
    else:
        logging.info(f"No color specified. Using random color = {COLOR}")

    if COLOR not in color_codes:
        logging.error(f"Unsupported color '{COLOR}'. Supported: {SUPPORTED_COLORS}")
        exit(1)

    app.run(host='0.0.0.0', port=81, debug=True)
