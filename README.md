# Rozlicz

Automatyczna księgowość dla e-commerce JDG. 400 zł netto, bez limitu faktur.

## Status

🚧 W budowie — MVP w przygotowaniu

## Opis

Rozlicz to zautomatyzowana księgowość dla jednoosobowych działalności gospodarczych prowadzących sprzedaż online (Allegro, Shopify, Amazon).

### Główne funkcje (MVP)
- Automatyczny import faktur z KSeF
- Podgląd podatków w czasie rzeczywistym (PIT, VAT, ZUS)
- Automatyczne generowanie deklaracji (ZUS DRA, JPK_VAT)
- Brak limitu dokumentów — stała cena 400 zł netto/miesiąc

## Tech Stack

- **Frontend:** Next.js 14, Tailwind CSS, shadcn/ui
- **Backend:** Python 3.12, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Queue:** Redis + Celery
- **Hosting:** Vercel (frontend), Railway (backend + DB)

## Struktura projektu

```
rozlicz/
├── apps/
│   ├── web/              # Next.js customer portal
│   └── admin/            # Internal back-office
├── services/
│   └── api/              # FastAPI backend
├── packages/
│   ├── ui/               # Shared UI components
│   ├── config/           # Shared config
│   └── ts-config/        # TypeScript configs
├── docs/                 # Documentation
└── infra/                # Infrastructure configs
```

## Development

### Wymagania
- Node.js 20+
- Python 3.12+
- Docker (opcjonalnie)

### Instalacja
```bash
# Frontend
cd apps/web
npm install
npm run dev

# Backend
cd services/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Roadmap

- [ ] Faza 0: Fundament (tydzień 1)
- [ ] Faza 1: Fake Door Test (tydzień 2-5)
- [ ] Faza 2: MVP Development (tydzień 6-10)
- [ ] Faza 3: Beta Launch (tydzień 11-14)

## Licencja

MIT
