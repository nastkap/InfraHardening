# InfraHardening - Managed Security Services Platform

**Komercyjna platforma do zarządzania bezpieczną infrastrukturą chmurową w Azure**

Automatyczna orkiestracja bezpiecznego środowiska hybrydowego w Azure z wykorzystaniem IaC, GitOps i automatycznej diagnostyki. Pełne rozwiązanie SaaS do sprzedaży jako usługa zarządzania bezpieczeństwem infrastruktury.

## Opis produktu

InfraHardening to kompleksowa platforma SaaS, która automatyzuje pełny cykl życia bezpiecznej infrastruktury w chmurze Azure. Rozwiązanie jest gotowe do komercyjnego wykorzystania jako usługa Managed Security Services dla małych i średnich firm.

### Wartość biznesowa

- **Model SaaS gotowy do sprzedaży**: Pełna platforma z systemem fakturowania, subskrypcji i obsługi klientów
- **Trzy plany cenowe**: Basic (500 zł), Pro (1500 zł), Enterprise (3000 zł) miesięcznie
- **Automatyzacja onboarding**: Klienci są automatycznie onboardowani po rejestracji
- **Multi-tenant**: Pełna izolacja danych i infrastruktury dla każdego klienta
- **Automatyczne raportowanie**: Generowanie raportów security, usage, cost i performance

## Architektura

### Provizjonowanie Infrastruktury (Terraform & Azure)
- Automatyczne tworzenie zasobów w Azure za pomocą kodu Terraform
- Odizolowane sieci wirtualne (VNet), podsieci (Subnets), bramy sieciowe oraz maszyny wirtualne z systemem Linux (AlmaLinux / Ubuntu)
- Definiowanie ścisłych reguł filtrowania ruchu na poziomie Network Security Groups (NSG) z ograniczeniem dostępu administracyjnego wyłącznie do protokołu SSH

### Automatyzacja Konfiguracji i Hardening (Ansible & Linux)
- Playbooki Ansible automatycznie instalujące zależności i konfigurujące systemy operacyjne po ich utworzeniu w chmurze
- Utwardzanie bezpieczeństwa (system hardening): wyłączenie logowania hasłem przez SSH, konfiguracja zapory firewalld/ufw, automatyczna aktualizacja pakietów i zarządzenie użytkownikami

### Diagnostyka i Integracja (Go, Python, Bash, REST API)
- Lekkie narzędzie w Go (Golang) uruchamiane na serwerach jako usługa systemowa (systemd), sprawdzające dostępność portów, trasowanie sieciowe oraz kondycję usług
- Skrypty orkiestrujące w Pythonie i Bashu, które komunikują się z Azure REST API w celu automatycznego pobierania aktualnych adresów IP i statusu maszyn w formacie JSON/YAML

### Potok CI/CD i GitOps (Jenkins, Groovy, GitHub Actions)
- Deklaratywny potok w Jenkinsie stworzony w języku Groovy (Jenkinsfile), odpowiadający za automatyczne testowanie kodu Terraform (terraform plan), uruchamianie zadań Ansible oraz wdrożenie
- GitHub Actions jako pierwsza linia weryfikacji: walidacja składni plików YAML/JSON, skanowanie bezpieczeństwa kodu oraz automatyczny linting przy każdym git push

### Monitoring i Wizualizacja (Grafana)
- Integracja serwerów z dashboardem w Grafanie, umożliwiająca podgląd metryk systemowych w czasie rzeczywistym oraz stałą weryfikację połączeń sieciowych

## Użyte technologie

| Obszar | Wykorzystane technologie / Narzędzia |
|--------|--------------------------------------|
| Chmura & IaC | Microsoft Azure (VNet, VM, NSG), Terraform |
| Konfiguracja & Linux | Ansible, Linux (AlmaLinux / Ubuntu), VirtualBox (do testów lokalnych) |
| Skrypty & Kod | Python, Go (Golang), Bash, Groovy (Jenkinsfile) |
| CI/CD & GitOps | Jenkins, GitHub Actions, Git |
| Formaty & API | YAML, JSON, Azure REST API |
| Sieć, Security & Monitoring | TCP/IP, SSH, DNS, HTTP/HTTPS, Grafana |

## Struktura projektu
```
.
├── README.md
├── terraform/              # Konfiguracja Terraform dla Azure
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
├── ansible/                # Playbooki Ansible
│   ├── site.yml
│   ├── roles/
│   └── inventory/
├── go-agent/               # Agent diagnostyczny w Go
│   ├── main.go
│   ├── systemd/
│   └── go.mod
├── scripts/                # Skrypty orkiestracyjne
│   ├── python/
│   └── bash/
├── jenkins/                # Konfiguracja Jenkins
│   └── Jenkinsfile
├── github-actions/         # Workflows GitHub Actions
│   └── .github/workflows/
├── grafana/                # Dashboardy Grafana
│   └── dashboards/
└── docs/                   # Dokumentacja
```

## Wymagania wstępne

- Konto Azure z odpowiednimi uprawnieniami
- Terraform >= 1.0
- Ansible >= 2.9
- Go >= 1.20
- Python >= 3.8
- Jenkins z zainstalowanymi pluginami
- Grafana
=

## Licencja

MIT License
