from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)  
UPLOAD_FOLDER = "./uploads"
OUTPUT_FOLDER = "./outputs"
DOCKER_IMAGE = "openqp/openqp:v1.0"  # Consistent image tag
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    """Home route to verify backend is running."""
    return "Welcome to the OpenQP Backend! Use the /submit-job endpoint for job submissions."

@app.route("/submit-job", methods=["POST"])
def submit_job():
    """Endpoint to handle job submissions."""
    try:
        system_name = request.form["systemName"]
        geometry = request.form["geometry"]
        input_content = request.form["input"]
        
        geo_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.xyz")
        inp_path = os.path.join(UPLOAD_FOLDER, f"{system_name}.inp")
        log_path = os.path.join(OUTPUT_FOLDER, f"{system_name}.log")
        
        # Write input files
        with open(geo_path, "w") as geo_file:
            geo_file.write(geometry)
        with open(inp_path, "w") as inp_file:
            inp_file.write(input_content)
        
        # Convert files to Unix format
        subprocess.run(["dos2unix", geo_path, inp_path], check=True)
        
        # Pull the Docker image
        pull_command = ["docker", "pull", DOCKER_IMAGE]
        subprocess.run(pull_command, check=True)
        
        # Prepare Docker run command
        docker_command = [
            "docker", "run", "-it", "--rm",
            "-v", f"{os.path.abspath(UPLOAD_FOLDER)}:/data",
            "-v", f"{os.path.abspath(OUTPUT_FOLDER)}:/results",
            DOCKER_IMAGE,
            "bash", "-c", f"cd /data && openqp {system_name}.inp"
        ]
        
        # Run the Docker container
        try:
            result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        except subprocess.CalledProcessError as e:
            print("Error occurred:", e)
            print("Error output:", e.output)
            return jsonify({
                "success": False, 
                "error": f"Docker command failed: {e}",
                "stdout": e.stdout,
                "stderr": e.stderr
            })
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return jsonify({"success": False, "error": "Log file not found."})
        
        # Read and return log file contents
        with open(log_path, "r") as log_file:
            log_content = log_file.read()
        
        return jsonify({"success": True, "logFile": log_content})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)