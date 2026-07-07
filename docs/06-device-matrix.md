# Device Matrix

## Policy

This matrix tracks project verification status. Official TP-Link support status must be checked through the official supported products page and model support pages.

## Fact

- The official OpenAPI guide lists `VIGI NVR1008H-8P( V1.20 )` in the article applicability list.
- The supported products page says listed and higher hardware versions of listed models are supported by VIGI Open API.
- The supported products page says latest firmware should be installed.
- TP-Link states that product availability varies by region and that the compatible device list may be updated.

## MVP Device

| Model | Hardware version | Firmware | OpenAPI status | Project verification | Known issues |
| --- | --- | --- | --- | --- | --- |
| VIGI NVR1008H-8P | `V1.20` from official guide applicability list | TODO | Official guide applicability list includes this model/version | Not verified yet | TODO |

## Candidate Devices From Official OpenAPI Guide Applicability List

These models appear in the official OpenAPI guide applicability list. Project support is not implied until tested.

| Model | Hardware version text from official guide | Project status |
| --- | --- | --- |
| VIGI NVR1008H | `V2.20` | TODO |
| VIGI NVR4064H | `V1` | TODO |
| VIGI NVR4032H | `V1` | TODO |
| VIGI NVR1004H | `V1` | TODO |
| VIGI NVR4016H | `V1` | TODO |
| VIGI NVR1008H-8MP | `V1.20` | TODO |
| VIGI NVR1016H | `V1.20` | TODO |
| VIGI NVR2008H-8MP | `V1 V2` | TODO |
| VIGI NVR2016H-16P | `V1 V2` | TODO |
| VIGI NVR1008H-8P | `V1.20` | MVP target |
| VIGI NVR1004H-4P | `V1` | TODO |
| VIGI NVR2016H | `V1.20 V2` | TODO |
| VIGI NVR1104H-4P | `V1` | TODO |
| VIGI NVR2016H-16MP | `V1 V2` | TODO |
| VIGI NVR1108H-W | `V1` | TODO |

## Verification States

| State | Meaning |
| --- | --- |
| `official-listed` | Listed in official TP-Link source. |
| `lab-planned` | A project maintainer plans to test the device. |
| `readonly-verified` | Read-only OpenAPI calls pass against hardware. |
| `mutating-verified` | Mutating OpenAPI calls pass against hardware. |
| `rtsp-verified` | Live/replay stream behavior is verified. |
| `unsupported` | Official or project verification says the device should not be supported. |

## Related Documents

- [02-references.md](02-references.md)
- [03-api-scope.md](03-api-scope.md)
- [05-test-strategy.md](05-test-strategy.md)
- [10-limitations.md](10-limitations.md)
- [11-roadmap.md](11-roadmap.md)
