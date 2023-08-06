VVault
==


# Stats
<img src="https://img.shields.io/pypi/dm/vvault?style=for-the-badge" alt="pypi">

Based on
* hvac
* vault

Start
==
poetry
```shell
poetry add vvault
```
pip
```shell
pip install vvault
```
import
```python
from vvault.vault import VaultMaster
```

Config for vault (services.yaml)
==
```yaml
---
environments:
  dev:
    services:
      db:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: '1'
        POSTGRES_BD: postgres
  prod:
    services:
      db:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: '1'
        POSTGRES_BD: postgres
policy:
  dev:
    db_access:
      path:
        dev/*:
          capabilities:
            - read
            - list
        dev/db/*:
          capabilities:
            - read
            - list
        sys/mounts/:
          capabilities:
            - read
            - list
  prod:
    db_access:
      path:
        dev/*:
          capabilities:
            - read
            - list
        dev/db/*:
          capabilities:
            - read
            - list
        sys/mounts/:
          capabilities:
            - read
            - list
acl:
  dev_db_cl:
    password: adminadminadmin
    polices:
      - 'dev/db_access'
  prod_db_cl:
    password: adminadminadmin
    polices:
      - 'dev/db_access'

```

Examples (first start)
==
```python
if __name__ == "__main__":
    vault = VaultMaster(
        url="http://localhost:8200", auth_methods=("approle", "userpass")
    )
    response = vault.start(
        root_token=None, unseal_keys=None, config_file=Path("services.yaml")
    )
    print(f"response: {response}")
```

Examples (ordinary start)
==
```python
if __name__ == "__main__":
    vault = VaultMaster(
        url="http://localhost:8200", auth_methods=("approle", "userpass")
    )
    response = vault.start(
        root_token="you_token",
        unseal_keys=('1_key', '1_key', '3_key'),
        config_file=Path("services.yaml"),
    )
    print(f"response: {response}")
```
