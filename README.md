A user-friendly, agent-based vulnerability scanning and reporting tool designed to automate security audits for IT auditors and cybersecurity professionals.

📌 Project Overview
The Basic Security Test Application or IT Auditor Helping Application is built to assist IT auditors in performing system and network vulnerability assessments with minimal technical overhead. With a ReactJS frontend and a FastAPI Python backend, it offers an efficient, intuitive interface and generates PDF audit reports.

🧰 Tech Stack
Frontend: ReactJS
Backend: Python (FastAPI)
Database: PostgreSQL

🚀 Features
🔍 Automated vulnerability scanning (system and network)
🧠 Minimal training required – user-friendly CLI and web UI
📄 Auto-generated PDF audit reports with mitigation suggestions
📡 Includes WPA/WPA2 wireless security testing
💾 Saves .JSON and .PDF reports locally
📊 Real-time scan logging
🌐 REST API and CLI agent integration

User Guide
1. installed (on macOS via Homebrew):
• brew install python@3.11
• node postgresql nmap tcpdump bind
• brew services start postgresql

2. Project Setup
• Unzip and enter the project directory

3. Database setup
• Create PostgreSQL role and database
• Apply the database schema
• Set up environment configuration

4. Start the Backend API
• Go to backend app directory.
• Create a python virtual environment named. venv in the current directory.
• Activate the virtual environment. Command - source .venv/bin/activate
• Upgrade the pip installer.
• Install the required backend libraries. Command use- pip install fastapi uvicorn databases[postgresql] sqlalchemy asyncpg python-dotenv reportla

5. Launch the API Server
• uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

6. Start the front-end
• Go to the front-end directory
• Install npm
• Start npm

7. Register Account
• Register as you are IT Auditor. Fill the required details about your IT Auditor’s details. After autogenerate an auditor’s code.

8. Then Go to the terminal, Install & Run the CLI Agent
cd ../agent
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install click requests rich reportlab psutil

9. In the agent terminal run this command,
python cli.py \
--auditor-code “ ” \
--server-url http://localhost:8000 \
--client-company “ ” \
--it-manager “ ”

10. Then go to the login page. Enter the auditor’s code given. Then, view the audit report or download a
report as a .pdf.

Future Enhancements
Cloud deployment (AWS integration)
Real-time alerts and notifications
Graph-based report visualizations
Advanced authentication and RBAC

🧑‍💻 Author
Pasidu Adithya Liyanage
BSc(Hons) Computer Security, University of Plymouth
