# Manifest Format

Schema `1.0.0` fields: dataset ID, explicit UTC cutoff, sorted unique record SHA-256 references, rejected count and manifest SHA-256. The hash covers canonical identity content and excludes wall-clock time and host paths. Repeated input at the same cutoff is identical.

**Limitation:** duplicate hashes are normalized rather than reported separately; verified reads and atomic create-only publication are required before release beyond synthetic demos.
