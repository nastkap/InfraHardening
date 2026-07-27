# InfraHardening - Managed Security Services Platform

**Komercyjna platforma SaaS do zarządzania bezpieczną infrastrukturą chmurową w Azure**

## Opis produktu

InfraHardening to kompleksowa platforma SaaS, która automatyzuje pełny cykl życia bezpiecznej infrastruktury w chmurze Azure. Rozwiązanie jest gotowe do komercyjnego wykorzystania jako usługa Managed Security Services dla małych i średnich firm.

### Wartość biznesowa

- **Model SaaS gotowy do sprzedaży**: Pełna platforma z systemem fakturowania, subskrypcji i obsługi klientów
- **Trzy plany cenowe**: Basic (500 zł), Pro (1500 zł), Enterprise (3000 zł) miesięcznie
- **Automatyzacja onboarding**: Klienci są automatycznie onboardowani po rejestracji
- **Multi-tenant**: Pełna izolacja danych i infrastruktury dla każdego klienta
- **Automatyczne raportowanie**: Generowanie raportów security, usage, cost i performance

## Komercyjne funkcje SaaS

### System Zarządzania Klientami
- **Multi-tenant Architecture**: Pełna izolacja danych i infrastruktury
- **Automatyczny Onboarding**: Klienci są automatycznie onboardowani po rejestracji
- **Dashboard Zarządzania**: Panel administracyjny do zarządzania klientami

### System Płatności
- **Integracja Stripe**: Obsługa płatności kartą i subskrypcji
- **Integracja Przelewy24**: Lokalne płatności dla polskich klientów
- **Automatyczne Fakturowanie**: Generowanie i wysyłanie faktur
- **Trzy Plany Cenowe**: Basic (500 zł), Pro (1500 zł), Enterprise (3000 zł)

### Automatyczne Raportowanie
- **Security Reports**: Raporty bezpieczeństwa i zgodności
- **Usage Reports**: Raporty wykorzystania zasobów
- **Cost Reports**: Raporty kosztów i optymalizacji
- **Performance Reports**: Raporty wydajności i uptime

### Monitoring i Diagnostyka
- **Go Agent**: Lekki agent monitorujący na każdym serwerze
- **Prometheus Metrics**: Zbieranie metryk w czasie rzeczywistym
- **Grafana Dashboards**: Wizualizacja metryk i alerting
- **Automatyczne Alerty**: Powiadomienia o problemach

## Model Biznesowy

### Plany Cenowe

| Plan | Cena Miesięczna | VMs | Użytkownicy | Support |
|------|-----------------|-----|-------------|---------|
| Basic | 500 zł | 3 | 5 | Email (9-17) |
| Professional | 1,500 zł | 10 | 20 | Chat 24/7 |
| Enterprise | 3,000 zł | 50 | 100 | Phone 24/7 |

### Przychody Potencjalne

- **10 klientów Basic**: 5,000 zł/msc → 60,000 zł/rok
- **10 klientów Pro**: 15,000 zł/msc → 180,000 zł/rok
- **5 klientów Enterprise**: 15,000 zł/msc → 180,000 zł/rok
- **Razem**: 35,000 zł/msc → **420,000 zł/rok**

## Jak uruchomić platformę SaaS

### 1. Baza danych PostgreSQL
```bash
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=infrahardening \
  -p 5432:5432 \
  postgres:15

# Zainicjuj schemat
psql -h localhost -U postgres -d infrahardening -f backend/database/schema.sql

# Zainicjuj schemat autentykacji
cd backend/auth
python auth_service.py
```

### 2. Backend API
```bash
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

### 4. Landing Page
```bash
# Otwórz landing/page/index.html w przeglądarce
# lub użyj prostego serwera HTTP
cd landing/page
python -m http.server 8080
```

### 5. Konfiguracja środowiskowa
```bash
# Ustaw zmienne środowiskowe
export DB_HOST=localhost
export DB_NAME=infrahardening
export DB_USER=postgres
export DB_PASSWORD=password
export JWT_SECRET_KEY=your-secret-key
export STRIPE_SECRET_KEY=sk_test_...
export P24_MERCHANT_ID=...
export P24_POS_ID=...
export P24_CRC=...
```

## Struktura projektu SaaS

```
.
├── README.md                    # Oryginalna dokumentacja
├── README-SAAS.md              # Ta dokumentacja SaaS
├── LICENSE                       # Licencja MIT
├── .gitignore                   # Git ignore
├── terraform/                    # Konfiguracja Terraform
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   └── tenant/             # Multi-tenant module
│   └── terraform.tfvars.example
├── ansible/                     # Playbooki Ansible
│   ├── site.yml
│   ├── ansible.cfg
│   ├── inventory/
│   └── roles/
├── go-agent/                    # Agent diagnostyczny w Go
│   ├── main.go
│   ├── go.mod
│   ├── systemd/
│   └── README.md
├── scripts/                     # Skrypty orkiestrujące
│   ├── python/
│   └── bash/
├── jenkins/                     # Konfiguracja Jenkins
│   ├── Jenkinsfile
│   └── README.md
├── github-actions/              # Workflows GitHub Actions
│   └── .github/
│       ├── workflows/
│       └── yamllint-config.yml
├── grafana/                     # Dashboardy Grafana
│   ├── dashboards/
│   └── datasources/
├── backend/                     # Backend API SaaS
│   ├── api/                     # FastAPI application
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── database/                # Schemat bazy danych
│   │   └── schema.sql
│   ├── billing/                 # System płatności
│   │   ├── stripe_integration.py
│   │   ├── przelewy24_integration.py
│   │   ├── billing_manager.py
│   │   └── requirements.txt
│   ├── reports/                 # System raportowania
│   │   ├── report_generator.py
│   │   └── requirements.txt
│   ├── onboarding/              # Automatyzacja onboarding
│   │   ├── onboarding_automation.py
│   │   └── requirements.txt
│   ├── auth/                    # System autentykacji
│   │   ├── auth_service.py
│   │   └── requirements.txt
│   └── config/                  # Konfiguracja
│       └── pricing.yaml        # Cennik i plany
├── frontend/                    # Frontend React Dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── landing/                     # Landing page dla klientów
│   └── page/
│       └── index.html
└── docs/                        # Dokumentacja
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    └── CONTRIBUTING.md
```

## Wymagania wstępne

- Konto Azure z odpowiednimi uprawnieniami
- Terraform >= 1.5
- Ansible >= 2.15
- Go >= 1.21
- Python >= 3.11
- Node.js >= 18
- PostgreSQL 15
- Stripe account (dla płatności)
- Przelewy24 account (opcjonalnie)

## Licencja

MIT License
