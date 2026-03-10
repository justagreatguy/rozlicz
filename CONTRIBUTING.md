# Contributing

## Git Workflow

1. **Main branch:** `main` — tylko stabilny kod
2. **Develop branch:** `develop` — integracja funkcji
3. **Feature branches:** `feature/nazwa-funkcji`

## Commit Messages

Format: `typ(scope): opis`

Typy:
- `feat:` — nowa funkcja
- `fix:` — naprawa błędu
- `docs:` — dokumentacja
- `style:` — formatowanie
- `refactor:` — refaktoryzacja
- `test:` — testy
- `chore:` — infrastruktura

Przykłady:
```
feat(auth): add JWT login endpoint
fix(ksef): handle empty invoice list
docs(api): update OpenAPI spec
```

## Code Review

- Wszystkie zmiany przez Pull Request
- Wymagane review: 1 osoba
- CI musi przechodzić

## Definition of Done

- [ ] Kod działa lokalnie
- [ ] Testy przechodzą
- [ ] Dokumentacja zaktualizowana
- [ ] Code review zatwierdzone
