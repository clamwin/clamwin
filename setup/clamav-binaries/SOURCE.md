# ClamAV Binary Source

This directory contains the prebuilt ClamAV payload used by the SignPath packaging workflow. The current files were staged from the sibling `binaries/clamav` payload in this workspace.

When updating these binaries, replace the four `clamav-*` directories together and regenerate `SHA256SUMS.txt` before running the signing workflow.