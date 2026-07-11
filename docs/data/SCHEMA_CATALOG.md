# Schema Catalog

The code contracts in `src/bharat_equity/domain/models.py` are authoritative for Phase 1 schema `1.0.0`. Units are explicit fields: currency for money/prices, `unit` for facts, volume as security quantity. Missing critical identity/source fields block use; missing optional end times mean open intervals. Corrections append revisions and set supersession time; raw evidence never mutates. Canonical serialization is JSON-compatible with Decimal strings and ISO timestamps.

**Open question:** field-level scale/quantization and a migration registry require independent approval before real provider mapping.
