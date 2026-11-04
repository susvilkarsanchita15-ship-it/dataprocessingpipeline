from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

# Get the project folder location
PROJECT_ROOT = Path(__file__).resolve().parent

# Location of employee JSON data
EMPLOYEE_FILE = PROJECT_ROOT / "data" / "input" / "employees.json"


class EmployeeAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Accept requests only for /employees
        if self.path != "/employees":
            self.send_error(404, "API endpoint not found")
            return

        try:
            # Read employee data from JSON file
            with EMPLOYEE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            # Convert data into JSON response
            response = json.dumps(data, indent=4).encode("utf-8")

            # Send successful response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()

            self.wfile.write(response)

        except (FileNotFoundError, json.JSONDecodeError) as error:
            self.send_error(500, str(error))


if __name__ == "__main__":

    # Start local API server on port 8000
    server = HTTPServer(("127.0.0.1", 8000), EmployeeAPIHandler)

    print("API running at http://127.0.0.1:8000/employees")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nAPI server stopped.")

    finally:
        server.server_close()