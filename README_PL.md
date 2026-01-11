# Home Assistant Automation Visualizer

Wizualizuj swoje automatyzacje Home Assistant jako interaktywne, responsywne diagramy HTML.

## Funkcje

- Wizualizacja workflow automatyzacji w czasie rzeczywistym
- Responsywny układ HTML/CSS - działa na każdym ekranie
- Każda automatyzacja wyświetlana jako osobna, interaktywna karta
- Auto-odświeżanie co 30 sekund
- Obsługa fallbacku połączeń
- Kolorowe logi z rotacją plików
- Czysta, modularna architektura

## Instalacja

### Development (Windows)

```powershell
# Utwórz wirtualne środowisko
python -m venv venv
.\venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Konfiguracja - utwórz plik .env
Copy-Item .env.example .env
# Edytuj .env i wpisz swój token z HA

# Uruchom
python app.py
```

### Produkcja (Raspberry Pi)

```bash
# Środowisko Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Konfiguracja - utwórz plik .env
cp .env.example .env
# Edytuj .env i wpisz swój token z HA

# Uruchom
python3 app.py
```

### Konfiguracja

Utwórz plik `.env` z szablonu:
```bash
cp .env.example .env
```

Edytuj `.env` i ustaw wartości:
- `HA_TOKEN` - Token długotrwały z Home Assistant (wymagane)
- `FLASK_PORT` - Port serwera (domyślnie: 5001)
- `DEBUG` - Tryb debugowania (domyślnie: False)

Jak uzyskać token HA: Ustawienia → Osoby → Twój użytkownik → Bezpieczeństwo → Tokeny długotrwałe

## Użycie

Otwórz w przeglądarce `http://localhost:5001` (lub IP Twojego RPi).

Strona automatycznie odświeża się co 30 sekund, lub kliknij "Refresh Now" dla ręcznej aktualizacji.

## Sprawdzanie portów

```bash
# Linux/macOS
sudo lsof -i :5001

# Windows
netstat -ano | findstr :5001
```

## Licencja

Licencja MIT - szczegóły w pliku LICENSE