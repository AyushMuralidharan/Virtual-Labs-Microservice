import requests
import json
import time
import os
import random
import string

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_response(response):
    """Print the response in a formatted way."""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 80)

def generate_random_string(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def test_version_control_api():
    """Test the version control API endpoints with comprehensive scenarios."""

    # Check if the service is running
    print("\n🚀 CHECKING IF THE SERVICE IS RUNNING...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)

    # Generate a unique repository name
    repo_name = f"college-project-{generate_random_string()}"

    # Create a repository
    print(f"\n📁 CREATING REPOSITORY '{repo_name}'...")
    response = requests.post(f"{BASE_URL}/repos/{repo_name}")
    print_response(response)

    # List repositories
    print("\n📋 LISTING ALL REPOSITORIES...")
    response = requests.get(f"{BASE_URL}/repos")
    print_response(response)

    # List branches in the new repository
    print(f"\n🌿 LISTING BRANCHES IN '{repo_name}'...")
    response = requests.get(f"{BASE_URL}/repos/{repo_name}/branches")
    print_response(response)

    # Create multiple branches
    branches = ["development", "feature/user-auth", "feature/payment-gateway"]
    for branch_name in branches:
        print(f"\n🌿 CREATING BRANCH '{branch_name}'...")
        response = requests.post(
            f"{BASE_URL}/repos/{repo_name}/branches",
            json={"name": branch_name, "source_branch": "main"}
        )
        print_response(response)

    # List all branches after creation
    print(f"\n🌿 LISTING ALL BRANCHES IN '{repo_name}'...")
    response = requests.get(f"{BASE_URL}/repos/{repo_name}/branches")
    print_response(response)

    # Add files to the main branch
    print("\n📝 ADDING PROJECT STRUCTURE FILES TO MAIN BRANCH...")

    # Add README.md
    readme_content = f"# {repo_name.replace('-', ' ').title()}\n\nA college project demonstrating version control concepts.\n\n## Features\n\n- User Authentication\n- Payment Gateway Integration\n- Data Analytics Dashboard\n"
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/README.md",
        json={
            "content": readme_content,
            "commit_message": "Add project README with features list",
            "author_name": "Student Developer",
            "author_email": "student@college.edu"
        }
    )
    print_response(response)

    # Add requirements.txt
    requirements_content = "flask==2.0.1\npytest==6.2.5\npandas==1.3.3\nnumpy==1.21.2\nmatplotlib==3.4.3\n"
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/requirements.txt",
        json={
            "content": requirements_content,
            "commit_message": "Add initial project dependencies",
            "author_name": "Student Developer",
            "author_email": "student@college.edu"
        }
    )
    print_response(response)

    # Add app.py
    app_content = """from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({'status': 'online'})

if __name__ == '__main__':
    app.run(debug=True)
"""
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/app.py",
        json={
            "content": app_content,
            "commit_message": "Add main application file",
            "author_name": "Student Developer",
            "author_email": "student@college.edu"
        }
    )
    print_response(response)

    # Switch to development branch
    print("\n🔄 SWITCHING TO DEVELOPMENT BRANCH...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/checkout",
        params={"branch": "development"}
    )
    print_response(response)

    # Add development-specific files
    print("\n📝 ADDING DEVELOPMENT CONFIGURATION...")
    dev_config_content = """{
    "debug": true,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "dev_database",
        "user": "dev_user"
    },
    "logging": {
        "level": "DEBUG",
        "file": "logs/dev.log"
    }
}
"""
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/config/dev_config.json",
        json={
            "content": dev_config_content,
            "commit_message": "Add development configuration",
            "author_name": "DevOps Engineer",
            "author_email": "devops@college.edu"
        }
    )
    print_response(response)

    # Switch to user-auth feature branch
    print("\n🔄 SWITCHING TO USER AUTHENTICATION FEATURE BRANCH...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/checkout",
        params={"branch": "feature/user-auth"}
    )
    print_response(response)

    # Add user authentication files
    print("\n📝 IMPLEMENTING USER AUTHENTICATION FEATURE...")
    auth_module_content = """from flask import Blueprint, request, jsonify, session
import hashlib
import uuid

auth_bp = Blueprint('auth', __name__)

# Mock user database
users = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if username in users:
        return jsonify({'error': 'Username already exists'}), 409

    # Hash the password
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    users[username] = {
        'salt': salt,
        'password': hashed_password
    }

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if username not in users:
        return jsonify({'error': 'Invalid credentials'}), 401

    user = users[username]
    hashed_password = hashlib.sha256(user['salt'].encode() + password.encode()).hexdigest()

    if hashed_password != user['password']:
        return jsonify({'error': 'Invalid credentials'}), 401

    session['username'] = username
    return jsonify({'message': 'Login successful'}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200
"""
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/auth.py",
        json={
            "content": auth_module_content,
            "commit_message": "Implement user authentication module",
            "author_name": "Security Specialist",
            "author_email": "security@college.edu"
        }
    )
    print_response(response)

    # Switch to payment gateway feature branch
    print("\n🔄 SWITCHING TO PAYMENT GATEWAY FEATURE BRANCH...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/checkout",
        params={"branch": "feature/payment-gateway"}
    )
    print_response(response)

    # Add payment gateway files
    print("\n📝 IMPLEMENTING PAYMENT GATEWAY FEATURE...")
    payment_module_content = """from flask import Blueprint, request, jsonify
import uuid
import datetime

payment_bp = Blueprint('payment', __name__)

# Mock payment database
payments = {}

@payment_bp.route('/process', methods=['POST'])
def process_payment():
    data = request.get_json()
    amount = data.get('amount')
    card_number = data.get('card_number')
    expiry = data.get('expiry')
    cvv = data.get('cvv')

    if not all([amount, card_number, expiry, cvv]):
        return jsonify({'error': 'Missing payment information'}), 400

    # In a real application, you would integrate with a payment processor here
    # This is just a mock implementation

    # Generate a transaction ID
    transaction_id = str(uuid.uuid4())

    # Store the payment information (in a real app, you would store this securely)
    payments[transaction_id] = {
        'amount': amount,
        'card_last_four': card_number[-4:],  # Only store last 4 digits
        'status': 'completed',
        'timestamp': datetime.datetime.now().isoformat()
    }

    return jsonify({
        'transaction_id': transaction_id,
        'status': 'completed',
        'message': 'Payment processed successfully'
    }), 200

@payment_bp.route('/transactions', methods=['GET'])
def get_transactions():
    # In a real app, you would filter by user, etc.
    return jsonify({'transactions': list(payments.values())}), 200

@payment_bp.route('/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    if transaction_id not in payments:
        return jsonify({'error': 'Transaction not found'}), 404

    return jsonify(payments[transaction_id]), 200
"""
    response = requests.put(
        f"{BASE_URL}/repos/{repo_name}/files/payment.py",
        json={
            "content": payment_module_content,
            "commit_message": "Implement payment gateway module",
            "author_name": "Financial Systems Developer",
            "author_email": "finance@college.edu"
        }
    )
    print_response(response)

    # List all branches and their files
    for branch in ['main', 'development', 'feature/user-auth', 'feature/payment-gateway']:
        print(f"\n📋 LISTING FILES IN '{branch}' BRANCH...")
        response = requests.post(
            f"{BASE_URL}/repos/{repo_name}/checkout",
            params={"branch": branch}
        )

        response = requests.get(
            f"{BASE_URL}/repos/{repo_name}/files",
            params={"branch": branch}
        )
        print_response(response)

    # List all commits
    print("\n📜 LISTING ALL COMMITS...")
    response = requests.get(f"{BASE_URL}/repos/{repo_name}/commits")
    print_response(response)

    # Merge user-auth feature into development
    print("\n🔀 MERGING USER AUTHENTICATION FEATURE INTO DEVELOPMENT...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/merge",
        data={
            "source_branch": "feature/user-auth",
            "target_branch": "development",
            "commit_message": "Merge user authentication feature into development",
            "author_name": "Project Lead",
            "author_email": "lead@college.edu"
        }
    )
    print_response(response)

    # Merge payment-gateway feature into development
    print("\n🔀 MERGING PAYMENT GATEWAY FEATURE INTO DEVELOPMENT...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/merge",
        data={
            "source_branch": "feature/payment-gateway",
            "target_branch": "development",
            "commit_message": "Merge payment gateway feature into development",
            "author_name": "Project Lead",
            "author_email": "lead@college.edu"
        }
    )
    print_response(response)

    # Check development branch files after merges
    print("\n📋 CHECKING DEVELOPMENT BRANCH FILES AFTER MERGES...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/checkout",
        params={"branch": "development"}
    )

    response = requests.get(
        f"{BASE_URL}/repos/{repo_name}/files",
        params={"branch": "development"}
    )
    print_response(response)

    # Final merge of development into main (release)
    print("\n🚀 FINAL MERGE OF DEVELOPMENT INTO MAIN (RELEASE)...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/merge",
        data={
            "source_branch": "development",
            "target_branch": "main",
            "commit_message": "Release v1.0.0 - Merge development into main",
            "author_name": "Release Manager",
            "author_email": "release@college.edu"
        }
    )
    print_response(response)

    # Check main branch files after final merge
    print("\n📋 CHECKING MAIN BRANCH FILES AFTER RELEASE...")
    response = requests.post(
        f"{BASE_URL}/repos/{repo_name}/checkout",
        params={"branch": "main"}
    )

    response = requests.get(
        f"{BASE_URL}/repos/{repo_name}/files",
        params={"branch": "main"}
    )
    print_response(response)

    # Get diff between initial commit and final state
    print("\n🔍 VIEWING DIFF BETWEEN INITIAL AND FINAL STATE...")
    # First, get the commit history to find the first and last commit
    response = requests.get(f"{BASE_URL}/repos/{repo_name}/commits")
    commits = response.json().get("commits", [])

    if len(commits) >= 2:
        first_commit = commits[-1]["id"]  # First commit is the last in the list
        last_commit = commits[0]["id"]    # Last commit is the first in the list

        response = requests.get(
            f"{BASE_URL}/repos/{repo_name}/diff",
            params={"commit1": last_commit, "commit2": first_commit}
        )
        print("Diff between first and last commit:")
        print_response(response)

    print("\n✅ VERSION CONTROL API TEST COMPLETED SUCCESSFULLY!")
    print(f"\n📊 SUMMARY:\n- Repository: {repo_name}\n- Branches created: {', '.join(branches + ['main'])}\n- Features implemented: User Authentication, Payment Gateway\n- Development workflow demonstrated: Feature branches → Development → Main")

if __name__ == "__main__":
    # Wait for the API to be ready
    print("Waiting for the API to be ready...")
    time.sleep(5)

    try:
        test_version_control_api()
    except Exception as e:
        print(f"\n❌ ERROR DURING TEST: {str(e)}")
