# Ansible 실습 · Playbook에서 Role까지

**Linux 서버 설정을 Ansible 코드로 옮기고, 변수·템플릿·작업 분리·Role 의존성으로 재사용하는 과정을 정리한 실습 저장소입니다.** 웹 서버 배포, 방화벽 설정, 계정 관리, 시간 동기화와 하드웨어 정보 수집을 주제별 디렉터리에서 다룹니다.

대표 예제는 [가상 호스트 Role](09_roles_create/playbook.yml)입니다. 웹 서버 설정을 `myvhost`로 묶고, 의존 Role인 `myfirewall`로 방화벽을 준비합니다. 호스트 정보로 Apache 설정을 생성하고 설정 변경 시 Handler가 서비스를 재시작합니다.

## 주요 구현

| 주제 | 구현 내용 | 코드 |
|---|---|---|
| Role 의존성 | `myvhost` 실행 전에 `myfirewall`을 적용하고 HTTP·HTTPS 방화벽 서비스 등록 | [의존성](09_roles_create/roles/myvhost/meta/main.yml), [방화벽 작업](09_roles_create/roles/myfirewall/tasks/main.yml) |
| 호스트별 웹 설정 | 호스트명으로 문서 루트 생성, Jinja2로 HTTP 가상 호스트 설정 배포 | [작업](09_roles_create/roles/myvhost/tasks/main.yml), [템플릿](09_roles_create/roles/myvhost/templates/vhost.conf.j2) |
| 변경에 따른 재시작 | 설정 파일 변경 시 `notify`로 httpd 재시작 요청 | [Handler](09_roles_create/roles/myvhost/handlers/main.yml) |
| 작업과 확인 분리 | 패키지·방화벽·콘텐츠 작업을 파일로 나누고 localhost에서 HTTP 응답 검사 | [08_project](08_project/playbook.yml), [응답 검사](08_project/plays/test.yml) |
| 실패 처리 | `failed_when`으로 실패 조건을 만들고 `rescue`·`always` 동작 실습 | [06_job_control](06_job_control/playbook.yml) |
| 보고서 수집 | Facts의 메모리·BIOS·디스크 값을 파일에 기록하고 제어 노드로 가져오기 | [hwreport.yml](05_hwreport/hwreport.yml), [저장된 결과](05_hwreport/results/) |

## 실습 구성

주제별 디렉터리에서 실습을 선택합니다. 대부분 자체 `ansible.cfg`와 Inventory를 사용하지만, `03_inventory`는 Inventory 구성 예제이며 `05_facts`는 `inventory1`·`inventory2`를 `-i`로 선택합니다.

| 경로 | 내용 |
|---|---|
| `03_*` | Inventory 그룹 구성, 접속 설정, Ad-hoc 명령 준비 |
| `04_*` | 웹·DB 패키지와 서비스, 여러 Play 구성 |
| `05_*` | 변수·Facts·Vault, 호스트별 변수, 보고서 수집 |
| `06_*` | 조건·반복·Handler·실패 처리 |
| `07_*` | 파일 배포·수집, hosts·MOTD 템플릿 |
| [08_project/](08_project/) | Task·Playbook 파일 분리와 웹 응답 확인 |
| [09_roles_create/](09_roles_create/) | `myvhost`·`myfirewall`·`rollback-svc` 구성 |
| [09_roles/](09_roles/) · [09_role-collections/](09_role-collections/) | 시간 동기화 Role과 Collection 사용 |
| [09_roles_download/](09_roles_download/) | 외부 Role 설치·사용 예제 |

`09_role-collections/collections/ansible_collections/`와 `09_roles_download/roles/`에는 외부 배포물도 포함되어 있습니다. 각 배포물의 출처·라이선스는 해당 디렉터리에 보관되어 있습니다.

## 가상 호스트 예제 실행

제어 노드에 Ansible과 `ansible.posix` Collection이 필요합니다. 대상 서버는 DNF·systemd·firewalld를 사용하는 Linux 환경이며, 기본 접속 계정 `ansible`의 SSH 인증과 sudo 권한을 준비합니다.

저장소를 받은 뒤 해당 실습 디렉터리에서 실행합니다. [inventory](09_roles_create/inventory)의 호스트를 실제 실습 서버로 맞추고 이름 해석을 준비합니다.

```bash
git clone https://github.com/tjung03/ansible_repo.git
cd ansible_repo/09_roles_create
ansible --version
ansible-galaxy collection list
ansible-inventory --graph
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml
```

적용 결과는 대상 서버의 `/var/www/vhosts/<Inventory 호스트명>/`과 `/etc/httpd/conf.d/vhost.conf`에서 확인합니다. 템플릿의 `ServerName`은 대상의 `ansible_fqdn`을 사용합니다.

```bash
ansible webservers -b -m ansible.builtin.command -a 'httpd -t'
ansible webservers -b -m ansible.builtin.command -a 'systemctl is-active httpd'
```

브라우저에서는 대상 서버의 FQDN으로 HTTP 접속해 배포한 페이지를 확인합니다. [08_project의 검사 Play](08_project/plays/test.yml)는 지정한 HTTP·HTTPS URL의 응답 코드 200을 검사합니다. 이 검사는 `validate_certs: false`로 TLS 인증서 검증을 생략합니다.  [하드웨어 보고서 결과](05_hwreport/results/)에는 호스트별 수집 파일이 남아 있습니다.

## 실행 시 참고

- `restore_*.yml`과 `rollback-svc`는 실습 설정을 삭제하는 정리 작업입니다. 특히 [가상 호스트 정리 변수](09_roles_create/roles/rollback-svc/vars/main.yml)는 `/var/www/vhosts` 전체와 패키지를 삭제하고 firewalld도 중지하므로 전용 실습 VM에서 사용합니다.
- 하드웨어 보고서는 `ansible_devices.sda.size`를 읽습니다. 디스크명이 다른 환경은 수집 대상을 맞춰야 합니다.
- Vault 암호 파일(`vault-pass`)과 암호화할 계정 변수 파일은 로컬에서만 관리합니다. 암호화 예제를 실행할 때는 각 Playbook의 `vars_files` 경로에 새 실습 값으로 Vault 파일을 준비하고 `--ask-vault-pass`로 암호를 입력합니다. 계정 변수 파일은 Git 추적에서 제외되어 있으므로 실행 전에 생성해야 합니다.
- Vault 변수는 `05_exec-ansible-vault`의 `newusers` 목록(`name`, `pw`), `05_secret/create_user.yml`의 `username`·`pwhash`(암호 해시), `05_variables_facts`의 `webid`·`webpass`를 사용합니다. 웹 인증 파일 `05_variables_facts/files/htpasswd`도 로컬에서 생성하고 `webid`·`webpass`와 일치시킵니다.
- SSH 인증 로그 수집 예제는 [secure_log_backups.yml](07_files/secure_log_backups.yml)에 있습니다. 수집 결과 `07_files/secure-backups/`는 로컬에서만 보관합니다.

## 사용 기술과 호환성

| 항목 | 저장소 기준 |
|---|---|
| 자동화 | Ansible YAML, Jinja2, Inventory·Facts·Handler·Role |
| 대상 서비스 | Apache HTTP Server, MariaDB, firewalld, chrony |
| 포함된 Collection | `ansible.posix 2.2.0`, 해당 배포물의 Core 요구사항은 `>=2.16.0` |
| Collection 설치 경로 | requirements에 로컬 절대 경로와 실습망 HTTP 주소가 포함되어 있어 실행 환경에 맞춰 준비 필요 |
| 시간대 모듈 | `09_roles/configure_time.yml`의 `ansible.builtin.timezone`은 [공식 모듈명 `community.general.timezone`](https://docs.ansible.com/projects/ansible/latest/collections/community/general/timezone_module.html)으로 조정 필요 |

Collection 요구사항은 [포함된 runtime.yml](09_role-collections/collections/ansible_collections/ansible/posix/meta/runtime.yml)에서 확인할 수 있습니다. 시간 동기화 예제의 `community.general`은 [requirements.yml](09_role-collections/collections/requirements.yml)에 없으므로 별도로 준비합니다.
