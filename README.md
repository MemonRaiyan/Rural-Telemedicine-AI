# GramCare AI — Rural Telemedicine AI Platform

**Integrated with the Ayushman Bharat Digital Mission (ABDM) Sandbox**  
*Academic Capstone Prototype — B.Tech Engineering Project II*

> **Central Vision:** *"Healthcare should not depend on where a person lives."*

---

## 1. Project Overview & Architecture

GramCare AI is a full-stack, mobile-first rural telemedicine platform engineered for underserved communities in India. It bridges the gap between rural patients, medical specialists, hospitals/NGOs, and village representatives through a robust, low-bandwidth architecture.

### Original Core Innovations
1. **Doctor Trust & Rating System:** A verified-consultation locked rating engine with multi-attribute scoring (communication in vernacular, punctuality, explanation quality) and dynamic Doctor Trust Scores.
2. **Community Health Camp Network:** A bidirectional coordination ecosystem connecting village panchayats directly with healthcare providers (Village Request $\rightarrow$ Hospital Acceptance $\rightarrow$ Public Scheduling $\rightarrow$ Seat Registration $\rightarrow$ Social Impact Reporting).
3. **Three-Tier Clinical AI Subsystem:**
   - **NLP Multilingual Symptom Triage:** Extracts symptoms, duration, and severity in English, Hindi, and Gujarati, classifying urgency into `LOW`, `MODERATE`, `HIGH`, or `EMERGENCY`.
   - **Emergency Red-Flag Engine:** Prioritizes acute distress (chest pain, stroke symptoms, acute dyspnea) with immediate 108/112 emergency calling assistance.
   - **Medical Image Screening:** Computer vision preliminary screening for Chest Radiography (X-Ray) and Cutaneous/Dermatology lesions.
4. **ABDM / ABHA Sandbox Adapter:** Clean service abstraction (`AbhaService`, `ConsentService`, `HealthRecordExchangeService`) simulating ABHA linking and HIE-CM electronic consent workflows with immutable audit logging.
5. **Rural-First Design:** Toggleable "Rural Mode" simulating 2G networks, stripping heavy assets, flattening cards, and providing audio-first teleconsultation fallback.

---

## 2. Technical Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| **Database** | Relational SQLite with WAL Mode & Foreign Keys (PostgreSQL production-ready) |
| **Real-Time Layer** | WebSockets (`/ws/consultation/{id}`), WebRTC Signaling, In-Call Live Chat |
| **Clinical AI** | Custom Multilingual Rule & NLP Parser, Pillow Imaging Heuristics |
| **Security & Auth** | PBKDF2-HMAC-SHA256, PyJWT Tokens, Role-Based Access Control (RBAC), Audit Logger |
| **Frontend** | Responsive Mobile-First Single-Page Application, Tailwind CSS, FontAwesome 6 |
| **Internationalization** | Modular JSON locale packs (`/static/locales/en.json`, `hi.json`, `gu.json`) |
| **Testing & DevOps** | Pytest, TestClient, Docker, Docker Compose |

---

## 3. Demo Accounts & One-Click Login

GramCare AI provides a **Project Demo Evaluation Mode** on the homepage allowing evaluators to switch roles with a single click:

| Role | Demo Name | Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Patient** | Ramesh Patel | `patient@gramcare.in` | `password123` | AI Triage, Doctor Search, Teleconsultation, Ratings, Camp Registration, ABHA |
| **Doctor** | Dr. Anjali Patel | `anjali@gramcare.in` | `password123` | Patient Queue, Tele-session, Clinical Notes, Digital Rx, Camp Requests |
| **Hospital / NGO** | Shakti Community Hospital | `hospital@gramcare.in` | `password123` | Village Camp Requests, Publish Camps, Manage Capacity, Impact Reports |
| **Village Rep** | Sarpanch Bhavesh Patel | `village@gramcare.in` | `password123` | Submit Village Camp Requests, Track Community Approvals |
| **Administrator** | System Administrator | `admin@gramcare.in` | `password123` | Platform Analytics, Governance, Audit Logs, Reset Demo Database |

---

## 4. Quick Start & Local Execution

### Prerequisites
- Python 3.10+ (Python 3.14 compatible)
- `pip` or virtual environment tool

### Step 1: Clone and Setup Virtual Environment
```bash
git clone https://github.com/your-username/gramcare-ai.git
cd gramcare-ai

python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Database Seed Script
```bash
python -m backend.app.database.seed_data
```

### Step 4: Launch Backend Server
```bash
python app.py
```
*The application starts at `http://localhost:8000`.*

---

## 5. Automated Test Suite

Run the comprehensive pytest test suite covering Auth, RBAC, NLP Triage, Emergency Red-Flags, Medical Image Screening, Appointments, Camps, and ABDM Consents:

```bash
source venv/bin/activate
export PYTHONPATH=.
pytest -v tests/test_all.py
```

---

## 6. Full Demonstration Walkthrough (30 Steps)

1. **Open App:** Navigate to `http://localhost:8000`.
2. **Select Language:** Switch between English, हिन्दी, and ગુજરાતી using the top navigation selector.
3. **Toggle Rural Mode:** Click **Rural Mode** to observe the immediate low-bandwidth UI transformation (2G network indicator, stripped decorative assets).
4. **Login as Patient:** Click the **Patient (Ramesh Patel)** one-click card.
5. **Launch AI Triage:** Click **AI Symptom Check**.
6. **Enter Vernacular Symptoms:** Type `"2 દિવસથી તાવ અને ખાંસી છે"` or `"Fever and cough for 3 days"`.
7. **Run AI Triage:** Click **Run AI Clinical Triage**. Review Urgency (`MODERATE`), Suggested Department (`General Physician`), Summary, and Questions for Doctor.
8. **Emergency Red-Flag Test (Optional):** Enter `"Severe chest pain radiating to left arm"` to witness the immediate Red-Flag Emergency Banner with 108 calling assistance.
9. **Find Doctor:** Click **Find Suitable Doctor Now**; the directory automatically pre-filters for General Physicians.
10. **View Doctor Profile:** Click **Profile** on Dr. Anjali Patel to inspect the Doctor Trust Score (4.8 ★) and verified patient reviews.
11. **Book Appointment:** Select a date and time slot (e.g. 04:00 PM) and click **Confirm Free Rural Consultation**.
12. **Conflict Prevention:** Attempting to book the same slot returns an immediate conflict error preventing double-booking.
13. **Medical Image Screening:** Go back to Patient Home $\rightarrow$ click **Medical Image AI** $\rightarrow$ upload a chest X-Ray or skin photo $\rightarrow$ observe detected finding, confidence %, and clinical disclaimer.
14. **Check ABHA Status:** Scroll to the ABHA profile card $\rightarrow$ observe linked ID (`14-2394-3948-2938`) with ABDM Sandbox badge.
15. **Switch to Doctor:** Sign out and click the **Doctor (Dr. Anjali Patel)** demo card.
16. **Doctor Queue:** Doctor dashboard displays Today's Appointments and the patient in queue.
17. **Start Teleconsultation:** Click **Start Session**.
18. **Real-Time Room:** The consultation room opens with live connection indicators, audio-first toggle, camera/mic controls, and live chat.
19. **Live Chat:** Type a message in the chat panel; messages are transmitted via WebSockets and persisted in SQLite.
20. **Doctor Clinical Notes:** Switch to the **Clinical Notes** tab, enter diagnosis (`Acute Viral Bronchitis`), and click **Complete & Issue Prescription**.
21. **Leave Room:** Click the red phone button.
22. **Rate Doctor:** Logging back in as Patient automatically brings up **Rate Your Consultation** for the completed session.
23. **Submit Rating:** Submit a 5-star rating with category breakdown (Communication, Punctuality, Explanation). The Doctor Trust Score updates in real time.
24. **Community Health Camps:** Navigate to **Health Camps** $\rightarrow$ click **Register for Free Camp Seat** on an available camp $\rightarrow$ seat count updates immediately.
25. **Request a Camp:** Switch to the **Request a Camp** tab $\rightarrow$ submit a request for a village (e.g. Rampura, 150 expected patients).
26. **Switch to Hospital:** Sign out and log in as **Hospital (Shakti Community Hospital)**.
27. **Accept Request:** View the incoming village camp request and click **Accept & Schedule Camp**. The camp is immediately scheduled on the public directory.
28. **Switch to Admin:** Sign out and log in as **Administrator**.
29. **Audit Log & Governance:** Review system analytics (Total patients, verified doctors, camps, triage urgency distribution) and inspect the immutable security audit log.
30. **Reset Demo Data:** Click **Reset Demo Data** to restore the clean initial academic state.

---

## 7. REST API Reference

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health and environment check | No |
| `POST` | `/api/auth/login` | Email & password login (returns JWT) | No |
| `POST` | `/api/auth/demo-login/{role}` | 1-Click login for academic evaluation | No |
| `POST` | `/api/ai/triage` | Multilingual NLP symptom assessment | No |
| `POST` | `/api/ai/image-screening` | Computer vision screening (X-Ray / Derm) | Optional |
| `GET` | `/api/doctors` | Search verified doctors with filters | No |
| `GET` | `/api/appointments` | Get user's appointment schedule | Yes |
| `POST` | `/api/appointments` | Book appointment with conflict lock | Patient |
| `POST` | `/api/consultations/{id}/start` | Initialize teleconsultation session | Yes |
| `POST` | `/api/consultations/{id}/complete` | Finalize consultation and issue Rx | Doctor |
| `POST` | `/api/reviews` | Submit verified doctor rating | Patient |
| `GET` | `/api/camps` | List all community health camps | No |
| `POST` | `/api/camps/{id}/register` | Register for community camp seat | Patient |
| `POST` | `/api/camp-requests` | Submit village health camp request | Optional |
| `POST` | `/api/camp-requests/{id}/accept` | Accept village camp & schedule | Hospital/Doctor |
| `POST` | `/api/abdm/link-abha` | Simulate ABHA ID linking via sandbox | Patient |
| `POST` | `/api/abdm/request-consent` | Doctor requests health record consent | Doctor |
| `GET` | `/api/admin/stats` | Platform analytics & distribution | Admin |
| `GET` | `/api/admin/audit-logs` | Immutable security audit logs | Admin |

---

## 8. Docker Deployment

To run GramCare AI in a containerized environment:

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 9. Medical Safety & Disclaimer

> [!IMPORTANT]
> **Mandatory Medical Safety Notice:**  
> GramCare AI is an academic engineering prototype developed for demonstration and research purposes. All AI-generated triage summaries, urgency classifications, and computer vision screening results are preliminary aids and **do NOT replace diagnosis, clinical advice, or treatment by a licensed medical practitioner**.
> 
> In all emergency situations (e.g. acute chest pain, shortness of breath, sudden paralysis, severe hemorrhage), users are directed to contact emergency medical services (**Dial 108 or 112 in India**) or visit the nearest hospital casualty immediately.
