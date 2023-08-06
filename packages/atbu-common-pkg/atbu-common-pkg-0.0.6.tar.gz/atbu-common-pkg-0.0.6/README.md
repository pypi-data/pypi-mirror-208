# atbu-common-pkg (atbu.common) package
## Overview
The atbu.common package is used by the following projects:
- [ATBU Backup & Persistent File Information](https://github.com/AshleyT3/atbu) utility package (atbu-pkg).
- [ATBU Multiprocessing Pipeline](https://github.com/AshleyT3/atbu-mp-pipeline) package (atbu-mp-pipeline-pkg).

Included is support for the following:
- **AesCbcPaddingEncryptor** and **AesCbcPaddingDecryptor** for AES CBC encryption/decryption with padding, related buffering/retention taken care automatically.
- **MultiEncoderDecoder** to allow defining/processing of .json encoding/decoding for multiple classes.
- **Hasher** which wraps multiple Python hashers for creating multiple hashes at once.
- **SimpleReport** which creates a simple report where  columns are wrappers. This is used by ATBU to report errors, sometimes containing lengthy messages. Note, there is an excellent Python reporting package, [tabulate](https://github.com/astanin/python-tabulate) which offers extensive reporting... please see that first. This SimpleReport class was created because, at the time, certain wrapping capabilities were not yet released for the tabulate project.
- **Singleton** providing singleton support.
- **util_helpers** providing miscellaneous helper functions used by ATBU, such clearing files, detecting what could be a valid base64 string, and other miscellaneous tools.

The main purpose of this repo is to carve out of ATBU what is more general for use in other projects going forward.

## Setup
To install atbu-common-pkg:

```
pip install atbu-common-pkg
```

See source code for this and the other packages mentioned above for details and usage information.
