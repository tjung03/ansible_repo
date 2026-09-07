Changelog
=========

[1.0.1] - 2026-05-12
--------------------

### Bug Fixes

- fix: Use verbosity level 3 for no_log (#18)

### Other Changes

- refactor: use firewall role instead of module (#19)

[1.0.0] - 2026-05-07
--------------------

### New Features

- feat: Add Trustee quadlet and secret registration server (#2)
- feat: add role fingerprints to syslog (#13)
- feat: new variable `trustee_server_secure_logging` defaulting to `true` (#15)

### Other Changes

- ci: tox-lsr 3.17.0 - container test improvements, use ansible 2.20 for fedora 43 [citest_skip] (#1)
- ci: tox-lsr 3.17.1 - previous update broke container tests, this fixes them [citest_skip] (#3)
- test: ensure role gathers the facts it uses by having test clear_facts before include_role (#11)
- refactor: copy external files to role, copy containers to quay.io linux-system-roles (#12)
- ci: Bump actions/github-script from 8 to 9 (#14)
- docs: document role parameters [citest_skip] (#16)

