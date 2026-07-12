# Manifest Format

Schema `1.0.0` fields: dataset ID, explicit UTC cutoff, total input count, unique record count, duplicate count, sorted unique record SHA-256 references, rejected count and manifest SHA-256. Total input reconciles as unique plus duplicates plus rejected. The hash covers canonical identity content and excludes wall-clock time and host paths. Repeated input at the same cutoff is identical.

Duplicate hashes remain visible through `duplicate_count` and the `DUPLICATE_SOURCE_RECORD` hard-gate taxonomy. Evidence reads recompute and verify the requested digest. Publication uses a flushed temporary file and an exclusive atomic hard-link publish so existing content-addressed objects cannot be overwritten; this is the standard-library no-replace equivalent selected instead of an overwriting rename.
