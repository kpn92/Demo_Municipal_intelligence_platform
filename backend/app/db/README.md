# Database Layer

## Σκοπός

Ο φάκελος `db` περιέχει το database layer της εφαρμογής.

Εδώ οργανώνεται ο τρόπος με τον οποίο το backend συνδέεται με τη βάση δεδομένων και διαχειρίζεται τις sessions, το engine και το βασικό ORM setup.

## Τι περιέχει

- SQLAlchemy engine
- session factory
- base declarative class
- database dependencies για FastAPI
- κοινά DB-related helpers

## Ρόλος

Ο φάκελος αυτός είναι υπεύθυνος για την τεχνική σύνδεση της εφαρμογής με την PostgreSQL.

Δεν περιέχει επιχειρησιακή λογική.  
Ο ρόλος του είναι καθαρά infrastructural.

## Παραδείγματα μελλοντικών αρχείων

- `base.py`
- `session.py`
- `dependencies.py`

## Βασική αρχή

Οι ρυθμίσεις της βάσης και ο κύκλος ζωής των database sessions πρέπει να παραμένουν συγκεντρωμένα εδώ, ώστε να υπάρχει καθαρή και ελεγχόμενη πρόσβαση στα δεδομένα.