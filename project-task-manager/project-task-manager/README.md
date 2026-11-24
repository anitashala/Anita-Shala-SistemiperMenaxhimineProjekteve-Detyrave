# Sistem për Menaxhimin e Projekteve dhe Detyrave

Aplikacion web për menaxhimin e projekteve dhe detyrave të ekipeve të vogla.
Backend: Python + FastAPI + MySQL 8 + JWT/bcrypt. Frontend: HTML, CSS dhe JavaScript.

## Struktura

```
project-task-manager/
├── README.md
├── backend/
│   ├── app/            routes, services, schemas, dependencies, db
│   ├── migrations/     schema.sql dhe seed.py
│   ├── .env.example
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── pages/          login, projects, tasks, dashboard
    ├── css/style.css
    └── js/             api.js dhe logjika e secilës faqe
```

## Nisja hap pas hapi

Duhet: Python 3.10 ose më i ri, MySQL 8 dhe VS Code (ose çdo server statik).

### 1. Databaza

```
cd backend
mysql -u root -p < migrations/schema.sql
```

Kjo krijon databazën `task_manager` me 5 tabelat.

### 2. Backend-i

```
cd backend
python -m venv venv
venv\Scripts\activate          (Windows)     source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
copy .env.example .env         (Windows)     cp .env.example .env       (Mac/Linux)
```

Hap skedarin `.env` dhe vendos fjalëkalimin e MySQL dhe një `JWT_SECRET` të gjatë.

Plotëso të dhënat testuese (një herë):

```
python migrations/seed.py
```

Nise serverin:

```
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### 3. Frontend-i

Hap dosjen `frontend` në VS Code dhe nise `index.html` me **Live Server** (porta 5500).
Ose nga terminali:

```
cd frontend
python -m http.server 5500
```

Pastaj hap http://localhost:5500 (ose http://127.0.0.1:5500).

### Përdoruesit testues (fjalëkalimi: `Test1234!`)

| Email | Roli |
| --- | --- |
| ana@test.com | Owner i Projektit 1, anëtare e Projektit 2 |
| beni@test.com | Anëtar i Projektit 1 |
| clara@test.com | Owner i Projektit 2, jo anëtare e Projektit 1 (për testin e 403) |

## Probleme të zakonshme

- **Gabim CORS në shfletues:** adresa e frontend-it duhet të jetë te `CORS_ORIGINS` në `.env` (port 5500). Rinise backend-in pas ndryshimit.
- **"JWT_SECRET mungon":** nuk e ke krijuar `.env` nga `.env.example`.
- **Access denied për MySQL:** kontrollo `DB_USER` dhe `DB_PASSWORD` te `.env`.
- **Frontend-i nuk lidhet me serverin:** kontrollo që `uvicorn` është i ndezur dhe që `API_URL` te `frontend/js/api.js` përputhet me adresën e tij.
