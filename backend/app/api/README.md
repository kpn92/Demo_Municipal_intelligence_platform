# API Layer

## Σκοπός

Ο φάκελος `api` περιέχει το επίπεδο του HTTP API της εφαρμογής.  
Εδώ οργανώνονται τα endpoints που εκθέτει το backend προς το frontend ή άλλους clients.

Το API layer είναι υπεύθυνο για:

- route registration
- grouping των endpoints
- versioning
- σύνδεση των routes με τα services

## Τι πρέπει να περιέχει

- route modules
- API version folders
- endpoint definitions
- router aggregation

## Κανόνας σχεδίασης

Τα routes πρέπει να είναι όσο γίνεται ελαφριά.  
Δεν πρέπει να περιέχουν πολύπλοκη επιχειρησιακή λογική.

Ο ρόλος τους είναι:

1. να λαμβάνουν το request
2. να καλούν το κατάλληλο service
3. να επιστρέφουν το response

## Παράδειγμα μελλοντικών αρχείων

- `v1/health.py`
- `v1/employees.py`
- `v1/vehicles.py`
- `v1/sectors.py`
- `v1/assignments.py`