# Backend

## Σκοπός

Ο φάκελος `backend` περιέχει όλο το server-side κομμάτι της πλατφόρμας.  
Εδώ υλοποιείται ο βασικός πυρήνας της εφαρμογής: το API, η σύνδεση με τη βάση δεδομένων, τα data models, τα validation schemas και η επιχειρησιακή λογική.

Η πρώτη φάση του έργου επικεντρώνεται στο MVP του module **Καθαριότητα & Αποκομιδή**, με στόχο να δημιουργηθεί μια σταθερή και επεκτάσιμη αρχιτεκτονική για μελλοντικά modules.

## Τι περιέχει

- FastAPI application
- Ρυθμίσεις εφαρμογής
- Database connection logic
- SQLAlchemy ORM models
- Pydantic schemas
- Business services
- Environment configuration
- Python dependencies

## Δομή

- `app/` : κύριος application κώδικας
- `.env` : μεταβλητές περιβάλλοντος
- `requirements.txt` : εξαρτήσεις Python

## Στόχος αρχιτεκτονικής

Η δομή του backend ακολουθεί διαχωρισμό ευθυνών:

- API layer
- Business logic layer
- Data access / database layer
- Validation / schema layer

Αυτό επιτρέπει καλύτερη συντήρηση, ευκολότερη επέκταση και καθαρότερο κώδικα.

## Σημείωση

Η λογική του backend πρέπει να παραμένει ανεξάρτητη από το frontend, ώστε το API να μπορεί να χρησιμοποιηθεί και από web client και από μελλοντικές mobile ή τρίτες εφαρμογές.