import os
import subprocess
import platform
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "./uploads"
OUTPUT_FOLDER = "./uploads"  # Using a single folder for both input and output
DOCKER_IMAGE = "openqp/openqp:gui"

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/submit-job", methods=["POST"])
def submit_job():
    """Endpoint to handle job submissions."""
    try:
        # Gather input data
        system_name = request.form["systemName"]
        geometry = request.form["geometry"]
        input_content = request.form["input"]
        
        # Define file paths
        geo_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.xyz")
        inp_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.inp")
        log_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.log")

        # Write input files
        with open(geo_path, "w") as geo_file:
            geo_file.write(geometry)
        with open(inp_path, "w") as inp_file:
            inp_file.write(input_content)
        
        # Convert files to Unix format
        subprocess.run(["dos2unix", geo_path, inp_path], check=True)
        
        # Pull the Docker image
        subprocess.run(["docker", "pull", DOCKER_IMAGE], check=True)

        # Docker command to run OpenQP
        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(UPLOAD_FOLDER)}:/data",
            "-w", "/data",
            DOCKER_IMAGE,
            "/usr/local/bin/openqp",
            f"{system_name}.inp"
        ]

        # Execute the Docker command
        subprocess.run(docker_command, check=True, capture_output=True, text=True)

        # Verify the log file exists
        if not os.path.exists(log_path):
            return jsonify({"success": False, "error": "Log file not found."})

        # Read the log file contents
        with open(log_path, "r") as log_file:
            log_content = log_file.read()

        return jsonify({"success": True, "logFile": log_content})

    except subprocess.CalledProcessError as e:
        # Handle Docker command errors
        return jsonify({
            "success": False,
            "error": f"Docker command failed with code {e.returncode}.",
            "stdout": e.stdout,
            "stderr": e.stderr,
        })

    except Exception as e:
        # Handle general exceptions
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    # Start Flask app
    app.run(debug=True)

