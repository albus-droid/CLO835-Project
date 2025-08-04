from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- Environment variables (for K8s Secret/ConfigMap support) ---
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))
MY_NAME = os.environ.get("MY_NAME", "Your Name")

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_FILE = os.environ.get("S3_FILE")

# --- MySQL connection ---
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# --- Presigned S3 URL helper ---
def get_presigned_s3_url():
    if not S3_BUCKET or not S3_FILE:
        logging.error("S3_BUCKET or S3_FILE not set in environment!")
        return ""  # Optionally, return a fallback URL here
    s3 = boto3.client('s3')
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': S3_FILE},
            ExpiresIn=3600
        )
        logging.info(f"Generated presigned S3 URL: {url}")
        return url
    except Exception as e:
        logging.error(f"Failed to generate presigned URL: {e}")
        return ""

# --- Flask Routes ---

@app.route("/", methods=['GET'])
def home():
    url = get_presigned_s3_url()
    return render_template('addemp.html', background_url=url, name=MY_NAME)

@app.route("/about", methods=['GET'])
def about():
    url = get_presigned_s3_url()
    return render_template('about.html', background_url=url, name=MY_NAME)

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

    url = get_presigned_s3_url()
    return render_template('addempoutput.html', name=emp_name, background_url=url)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    url = get_presigned_s3_url()
    return render_template("getemp.html", background_url=url, name=MY_NAME)

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

    url = get_presigned_s3_url()
    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"],
                           location=output["location"], background_url=url, name=MY_NAME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
