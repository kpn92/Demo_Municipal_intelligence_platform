# Schemas

## Σκοπός

Ο φάκελος `schemas` περιέχει τα Pydantic schemas της εφαρμογής.

Τα schemas χρησιμοποιούνται για validation, serialization και deserialization των δεδομένων που εισέρχονται ή εξέρχονται από το API.

## Τι περιέχει

- request schemas
- response schemas
- create schemas
- update schemas
- read schemas
- validation rules

## Ρόλος

Τα schemas ορίζουν το συμβόλαιο επικοινωνίας του API.

Με απλά λόγια, καθορίζουν:

- τι δεδομένα επιτρέπεται να σταλούν στο backend
- τι δεδομένα επιστρέφονται στον client
- ποιο είναι το σωστό format κάθε payload

## Παραδείγματα μελλοντικών αρχείων

- `employee_schema.py`
- `vehicle_schema.py`
- `sector_schema.py`
- `assignment_schema.py`

## Βασική αρχή

Τα schemas δεν είναι database models.  
Ο ρόλος τους είναι να ελέγχουν και να διαμορφώνουν τα δεδομένα του API, όχι να ορίζουν πίνακες βάσης.