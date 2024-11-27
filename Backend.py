from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "./uploads"
OUTPUT_FOLDER = "./outputs"
DOCKER_IMAGE = "openqp/openqp:v1.0"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/submit-job", methods=["POST"])
def submit_job():
    try:
 
        system_name = request.form["systemName"]
        geometry = request.form["geometry"]
        input_content = request.form["input"]

        geo_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.xyz")
        inp_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.inp")
        log_path = os.path.join(OUTPUT_FOLDER, f"{system_name}.log")

        with open(geo_path, "w") as geo_file:
            geo_file.write(geometry)

        with open(inp_path, "w") as inp_file:
            inp_file.write(input_content)

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(UPLOAD_FOLDER)}:/data",
            "-v", f"{os.path.abspath(OUTPUT_FOLDER)}:/results",
            DOCKER_IMAGE,
            f"/data/{system_name}.inp"
        ]
        subprocess.run(docker_command, check=True)

        # Check if log file exists
        if not os.path.exists(log_path):
            return jsonify({"success": False, "error": "Log file not found."})

        # Return log file content
        with open(log_path, "r") as log_file:
            log_content = log_file.read()

        return jsonify({"success": True, "logFile": log_content})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
