# VIGI NVR OpenAPI V1.4 Reference

## Registration

| Item | Value |
| --- | --- |
| Official document title | `VIGI NVR Open API Document` |
| Version | `V1.4` |
| Vendor/provenance | TP-Link VIGI NVR OpenAPI document supplied as the local authoritative source for this review |
| Local development source | `D:\Download\VIGI NVR Open API Document_v1.4.pdf` |
| SHA-256 | `A4478689664F4F300FC5EA2F69A3BF40564D43A4A71D411D48FE13BF0F651E6A` |
| Review date | `2026-09-20` |
| Repository status | Metadata only; the vendor PDF is not committed |

The earlier project baseline was the official `V1.0` document. This `V1.4`
document is the latest reviewed contract for the implemented read-only, Phase
3A, and Phase 3B increments. Implementation status and real-device verification
remain separate claims in the delta, scope, and limitations documents.

## Update-history summary

The PDF's update-history table records:

- `V1.0`: initial release.
- `V1.1`: correction of the authentication response algorithm to SHA-256 and
  additional event subtypes.
- `V1.2`: recording-control interface.
- `V1.3`: module-list interface; channel-management updates for add, remove,
  scan, and snapshot; PTZ interface; additional event subtypes.
- `V1.4`: RTSP-device addition; audio capability interfaces; PTZ capability
  updates and batch capability; alarm-output additions/changes; error-code
  information update.

The PDF uses `RTPS` once in the V1.4 update-history text for the RTSP-device
addition, while the interface and URL sections use `RTSP`. This record follows
the documented interface spelling `RTSP`.

## Relevant sections reviewed

The review used the following PDF sections and printed page ranges. PDF page
numbers include the cover and directory pages; printed document page numbers
are shown where useful.

| Area | PDF section | Printed pages |
| --- | --- | --- |
| Revision history, transaction format, authentication | `1.2`, `2.1`, `2.2` | 2-5 |
| Event protocol and event server | `3`, `3.1`, `3.2`, `4.8` | 5-6, 41-44 |
| Token and module discovery | `4.1.1`, `4.1.2` | 6-10 |
| Channel management and snapshot | `4.2` | 10-15 |
| Video and time | `4.3`, `4.4` | 15-23 |
| Audio | `4.5` | 23-27 |
| Disk and PoE | `4.6`, `4.7` | 27-41 |
| Recording and system control | `4.9`, `4.10` | 44-52 |
| PTZ, disarming, active defense, alarm output | `4.11`-`4.14` | 53-73 |
| Live/replay RTSP and talk | `5` | 74-77 |

## Source handling and contract rule

The local vendor PDF is a development-time reference only and is intentionally
not copied into this public repository. Do not add it, or a renamed copy of it,
to Git. The local path and hash above identify the source used for this review.

Future implementation must use documented contracts only: documented methods,
paths or protocol forms, request fields, response fields, and authentication
expectations. If the PDF does not establish a fact, the SDK documentation must
label it `UNKNOWN / NOT ENOUGH EVIDENCE` or `not documented` and must not fill
the gap with device folklore or reverse engineering.

See [the V1.0-to-V1.4 delta](nvr-openapi-v1.0-to-v1.4-diff.md) and the project
[reference register](../02-references.md).
