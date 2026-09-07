# trustee_server

[![ansible-lint.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/ansible-lint.yml) [![ansible-test.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/ansible-test.yml) [![codespell.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/codespell.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/codespell.yml) [![markdownlint.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/markdownlint.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/markdownlint.yml) [![qemu-kvm-integration-tests.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/qemu-kvm-integration-tests.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/qemu-kvm-integration-tests.yml) [![shellcheck.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/shellcheck.yml) [![tft.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/tft.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/tft.yml) [![tft_citest_bad.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/tft_citest_bad.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/tft_citest_bad.yml) [![woke.yml](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/woke.yml/badge.svg)](https://github.com/fedora.linux_system_roles.trustee_server/actions/workflows/woke.yml)

![trustee_server](https://github.com/fedora.linux_system_roles.trustee_server/workflows/tox/badge.svg)

An Ansible role that deploys [Trustee](https://confidentialcontainers.org/docs/attestation/) server components for confidential computing. Trustee provides attestation and secret delivery services (KBS, AS, RVPS) for workloads running in Trusted Execution Environments (TEEs).

## Features

- **Trustee Server (Quadlet)**: Deploys Trustee Key Broker Service(KBS), Attestation Service(AS) and Reference Value Provider Service(RVPS) using Podman Quadlets from a GitHub repository
- **Secret Registration Server**: HTTPS service that receives attestation-backed registration requests, verifies attestation, creates disk encryption keys, and stores them in Trustee KBS

## Requirements

### Control node

- Ansible 2.9 or later
- Install collection dependencies:

```bash
ansible-galaxy collection install -r meta/collection-requirements.yml
```

## Variables

### trustee_server_trustee

Whether to deploy the Trustee server components (KBS, AS, RVPS) using Podman
Quadlets.

The secret registration server is only deployed when this is `true` and
[`trustee_server_secret_registration_enabled`](#trustee_server_secret_registration_enabled)
is `true`.

Default: `true`

Type: `bool`

### trustee_server_secret_registration_enabled

Whether to deploy the secret registration HTTPS service that receives
attestation-backed registration requests, verifies attestation, creates disk
encryption keys, and stores them in Trustee KBS.

This has no effect unless [`trustee_server_trustee`](#trustee_server_trustee)
is `true`, because the registration server depends on Trustee.

Default: `false`

Type: `bool`

### trustee_server_secret_registration_listen_port

TCP port on which the secret registration server listens. The role opens this
port in firewalld.

Default: `8081`

Type: `int`

### trustee_server_secure_logging

If `true`, suppress potentially sensitive output from tasks that handle
credentials, secrets, and other sensitive data by setting `no_log: true` on
those tasks. This prevents passwords, API tokens, private keys, and similar
sensitive information from appearing in Ansible logs and console output.

If you need to debug issues with credential handling or secret management, you
can temporarily set `trustee_server_secure_logging: false` to see the full output from
these tasks. However, be aware that this may expose sensitive information in
logs, so it should only be used in development or troubleshooting scenarios.

Default: `true`

Type: `bool`

## Example Playbook

```yaml
- name: Deploy Trustee Server
  hosts: all
  vars:
    trustee_server_trustee: true
    trustee_server_secret_registration_enabled: true
    trustee_server_secret_registration_listen_port: 8081
  roles:
    - fedora.linux_system_roles.trustee_server
```

More examples are in the [`examples/`](examples) directory.

## Trustee Server

When enabled, the role:

1. Installs the Podman Quadlets provided by the role
2. Generates all required certificates of Trustee server components
3. Add KBS port 8080 to firewalld
4. Enables the services by default

Note that KBS listens on port 8080 which may require additional network security allowance depending on your environment.

## Secret Registration Server

When enabled, the secret registration server:

1. Listens for `POST /register-encryption-key` with `attestation_token` and `client_id` (machine-id)
2. Verifies the attestation token (Azure TPM-based)
3. Creates a disk encryption key and stores it in Trustee KBS
4. Appends resource policy to `/etc/trustee/kbs/policy.rego`

Clients can then fetch the key from Trustee CDH using attestation.

## License

MIT

## Author

Li Tian <litian@redhat.com>
