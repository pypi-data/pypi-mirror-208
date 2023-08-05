# wfetch-cli

To install:
```
pip install wfetch-cli
```

## Description

`wfetch-cli` is a tool for reliable downloading of files from the internet.

- Tool downloads files from the internet.
- Uses .netrc for authentication.
- Optionally expected file sha256 can be supplied. The tool will verify downloaded file hash, and will fail if it does not match.
- If file exists, and hash matches, it won't be downloaded.
