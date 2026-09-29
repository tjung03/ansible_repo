# 현행 Ansible 환경에서 실습하기

이 저장소는 RHCE 학습 흐름에 맞춰 Inventory, Playbook, 변수와 Facts, 작업 제어, 파일 배포, 프로젝트 분리, Role을 각각 연습하는 저장소다. 각 번호 디렉터리는 독립 실습 단위이며, 전체를 한 번에 적용하는 단일 애플리케이션은 아니다.

## 먼저 구분할 것

- `03_*`~`09_*` 디렉터리는 학습 당시의 문법과 실행 환경을 보존한 실습 스냅샷이다.
- `inventory`, `ansible.cfg`, 고정 주소와 계정명은 예시 환경 기준이다. 실행 전에 별도 실습 VM에 맞춘다.
- `restore_*.yml`, `rollback-svc`와 `00_poweroff`는 서비스·패키지·파일을 제거하거나 시스템을 종료할 수 있다. 전용 실습 환경에서 대상과 `--limit` 값을 먼저 확인한다.
- 일부 계정·DB 예제에는 학습용 고정 문자열이나 평문 변수 파일이 있다. 특히 `05_secret/secret2.yml`, `07_files/secret2.yml`과 DB 사용자 생성 예제의 값을 실제 비밀번호로 재사용하지 않고, 로컬 Vault 파일로 교체한다.

## 실습 준비와 정적 검증 환경

먼저 제어 노드에서 제공하는 Ansible 버전과 필요한 Collection의 호환성을 확인한다. 예를 들어 [RHEL 10의 System Roles 환경](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/introduction-to-rhel-system-roles)은 `ansible-core 2.16`을 제공한다. 아래 가상 환경의 `2.21.4`는 **2026-09-29에 수행한 정적 검증을 재현하기 위한 예시**이며, 모든 RHEL/RHCE 실습 환경의 권장 버전을 뜻하지 않는다. 다른 환경에서는 배포판 또는 Automation Platform의 지원 범위와 [공식 유지보수 표](https://docs.ansible.com/projects/ansible/latest/reference_appendices/release_and_maintenance.html)를 확인해 버전을 선택한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "ansible-core==2.21.4"
```

원본 FQCN을 그대로 실행하려면 다음 Collection이 필요하다. `community.mysql`의 현재 배포물은 `ansible.mysql`로 연결되는 호환 리디렉션을 제공하므로 두 Collection을 함께 준비한다. 신규 MySQL 코드는 `ansible.mysql`을 사용한다. 신규 MariaDB 코드에서는 [MariaDB 전용 Collection](https://docs.ansible.com/projects/ansible/latest/collections/ansible/mariadb/mariadb_user_module.html)을 확인한다. `ansible.mysql`은 6.0.0부터 MariaDB 지원을 중단할 예정이다.

```bash
ansible-galaxy collection install \
  ansible.posix \
  community.general \
  community.mysql \
  ansible.mysql
```

`09_roles/configure_time.yml`은 운영체제 패키지가 제공하는 `rhel-system-roles.timesync`를 호출한다. RHEL에서는 해당 System Role을 먼저 설치한다. Collection 방식으로 바꿀 때는 설치한 배포판에 맞는 Role FQCN과 변수명을 그 Collection 문서에서 확인한다.

```bash
sudo dnf install rhel-system-roles
```

## 실행 전 점검

한 실습 디렉터리로 이동한 뒤 Inventory와 설정을 먼저 확인한다.

```bash
cd 09_roles_create
ansible --version
ansible-galaxy collection list
ansible-inventory --graph
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml --list-hosts --limit webservers
ansible-playbook playbook.yml --check --diff --limit webservers
ansible-playbook playbook.yml --limit webservers
```

`--syntax-check`는 YAML과 Playbook 구성을 확인하지만 대상 OS 패키지, Python 라이브러리, sudo 권한, 네트워크 도달성까지 검증하지는 않는다. `--check` 역시 모든 모듈이 완전한 예측 실행을 지원하는 것은 아니므로 결과를 실제 적용과 동일하게 간주하지 않는다.

## 현재 이름과의 대응

| 저장소의 기존 표기 | 현행 사용 시 확인할 표기 | 설명 |
|---|---|---|
| `ansible.builtin.timezone` | `community.general.timezone` | `community.general` 설치 필요 |
| `ansible.builtin.selinux` | `ansible.posix.selinux` | `ansible.posix` 설치 필요 |
| `community.mysql.mysql_user` | MySQL: `ansible.mysql.mysql_user` / MariaDB: `ansible.mariadb.mariadb_user` | 기존 실습은 MariaDB를 사용한다. `community.mysql`은 호환 리디렉션 후 제거 예정이며, MariaDB 신규 코드는 전용 Collection을 확인 |
| `rhel-system-roles.timesync` | 설치 방식에 따라 기존 Role명 또는 Collection FQCN | RHEL 패키지 설치와 Galaxy Collection 설치를 혼용하지 않음 |
| `ansible.builtin.systemd` | `ansible.builtin.systemd_service` | 기존 이름은 현재 유효한 별칭 |

공식 참고 문서: [Ansible 설치](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html) · [Ansible Role](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html) · [ansible.posix](https://docs.ansible.com/projects/ansible/latest/collections/ansible/posix/index.html) · [community.general](https://docs.ansible.com/projects/ansible/latest/collections/community/general/index.html) · [ansible.mysql](https://docs.ansible.com/projects/ansible/latest/collections/ansible/mysql/index.html) · [ansible.mariadb](https://docs.ansible.com/projects/ansible/latest/collections/ansible/mariadb/index.html) · [RHEL System Roles](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/introduction-to-rhel-system-roles)

## 정적 검증 범위

2026-09-29에 다음을 확인했다.

- 외부 Collection 전체 소스는 제외하고, 저장소 작성 YAML 159개를 파싱했으며 YAML 오류는 없었다.
- `ansible-core 2.21.4`와 저장소에 포함된 `ansible.posix`, `community.general`, `fedora.linux_system_roles`를 사용해 실행형 Playbook 후보 64개를 검사했다.
- 58개는 `--syntax-check`를 통과했다.
- 2개는 별도 MySQL Collection, 2개는 OS 제공 `rhel-system-roles.timesync`, 2개 Role 내부 테스트는 테스트용 Role 검색 경로가 있어야 해 검사 환경에서 해석되지 않았다.

따라서 실패 6개를 곧바로 Playbook 문법 오류로 해석하면 안 된다. 필요한 Collection·Role·검색 경로를 준비한 다음 해당 실습 디렉터리에서 다시 검사해야 한다.
