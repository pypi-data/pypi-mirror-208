from pathlib import Path
from typing import Any

import hvac
import yaml  # type: ignore

from hvac.exceptions import InvalidRequest, InvalidPath
from requests.exceptions import InvalidSchema  # type: ignore

from vvault.logger import logger


class VaultMaster:
    def __init__(self, url: str, auth_methods: tuple[str, ...]):
        self.url = url
        self.client = hvac.Client(url=self.url)
        self._auth_methods: tuple[str, ...] = auth_methods

        logger.info(f"Connecting to: {self.url}")

    @property
    def sealed(self):
        return self.client.seal_status.get("sealed")

    @property
    def initialized(self):
        return self.client.seal_status.get("initialized")

    @property
    def auth_methods(self) -> list[str]:
        return list(self.client.sys.list_auth_methods().keys())

    @property
    def polices(self):
        return self.client.sys.list_policies()

    @property
    def userpasses(self) -> list:
        userpass_data = self.client.auth.userpass.list_user()
        return userpass_data.get("data", {}).get("keys")

    def __initialize(self):
        ...

    def __unseal(self):
        logger.info("Unsealing")
        self.client.sys.submit_unseal_keys(self.__unseal_keys[0:3])
        logger.info(f'initialized: {self.client.seal_status.get("initialized")}')
        logger.info(f'sealed: {self.client.seal_status.get("sealed")}')
        self.client = hvac.Client(url=self.url, token=self.__root_token)
        logger.info(
            f"Client authenticated (master token): {self.client.is_authenticated()}"
        )

        # enable auth methods
        self.enable_auth_methods(auth_methods=self._auth_methods)

    def start(
        self,
        config_file: Path,
        unseal_keys: tuple[str, ...] | None = None,
        root_token=None,
        update: bool = False,
    ) -> dict:
        """
        :param config_file: required
        :param unseal_keys:
        :param root_token: optional, if it's not first start
        :param update: optional, set True if we need updates from config
        """

        if not config_file.exists():
            raise FileNotFoundError(f"No config file by path: {config_file}")

        self.__parse_config_file(config_file)
        start_response = self.__start(
            root_token=root_token, unseal_keys=unseal_keys, update=update
        )
        return start_response

    def __parse_config_file(self, config_file: Path) -> None:
        logger.info(f"Config exists: {config_file}")
        with open(config_file) as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise AttributeError(f"Error parsing config file: {exc}")

    def __init(self) -> None:
        """
        :return:
        """
        logger.info("Initializing")
        vault_init_data: dict[str, Any] = self.client.sys.initialize(5, 3)
        # Get vault init data
        self.__unseal_keys: tuple[str, ...] = tuple(
            vault_init_data.get("keys", None)
        )  # type: ignore
        self.__root_token = vault_init_data.get("root_token", None)
        logger.info(f"root token: {self.__root_token}")
        logger.info(f"unseal keys (5): {self.__unseal_keys}")

    def __init_config(self) -> None:
        """
        config settings to vault
        """

        # set kv
        logger.info("Start Installing ENVS")
        kv_config: dict[str, dict] = self.config.get("environments")
        for contour in kv_config:
            logger.info(f"Installing env: {contour}")
            self.create_kv_area(contour)
            services: dict = kv_config.get(contour).get("services")  # type: ignore
            for service in services:
                service_config: dict = services.get(service)  # type: ignore
                self.set_kv_secret(
                    area=contour, context=f"{service}/config", data=service_config
                )
        logger.info("Finished Installing ENVS")

        # create polices
        logger.info("Start Creating Polices")
        policy: dict = self.config.get("policy")
        if not policy:
            return
        for contour in policy:
            contour_settings: dict = policy.get(contour)  # type: ignore
            for service in contour_settings:
                service_settings: dict = contour_settings.get(service)  # type: ignore
                self.create_policy(
                    area=f"{contour}/{service}", service=service_settings
                )
        logger.info("Finished Creating Polices")

        logger.info("Starting Creating UserPass")
        # create userpass
        acls: dict = self.config.get("acl", None)
        if not acls:
            return
        for acl in acls:
            acl_data: dict = acls.get(acl)  # type: ignore
            self.create_userpass(
                username=acl,
                password=acl_data.get("password"),  # type: ignore
                policies=acl_data.get("polices", []),
            )  # type: ignore
        logger.info("Finished Creating UserPass")

    def enable_auth_methods(self, auth_methods: tuple[str, ...]) -> None:
        for method in auth_methods:
            if f"{method}/" in self.auth_methods:
                logger.info(f"Skipping auth method: {method}, already enabled.")
                continue
            try:
                method_enabled = self.client.sys.enable_auth_method(method_type=method)
            except Exception as ex:
                logger.error(f"Fails when try to enable auth method {method} ex: {ex}")
                return

            logger.info(f"{method} enabled: {method_enabled.status_code == 204}")

    def create_kv_area(self, name: str) -> None:
        try:
            kv_v2_created = self.client.sys.enable_secrets_engine(
                "kv", path=name, options={"version": 2}
            )
        except InvalidRequest as ex:
            logger.info(f"Fails when try to create kv area: {ex}")
            return
        logger.info(f"kv_v2_created {name}: {kv_v2_created.status_code == 204}")

    def list_secrets(self, area, context=None) -> list:
        if context is None:
            context = ""
        try:
            response = self.client.secrets.kv.v2.list_secrets(
                mount_point=area, path=context
            )
        except Exception as ex:
            logger.warn(f"Fails when try to get list: {area, context}, ex: {ex}")
            response = {}
        data = response.get("data", {})
        return data.get("keys", [])

    def read_secret(self, area, context) -> dict:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                mount_point=area, path=context, raise_on_deleted_version=True
            )
        except InvalidPath as ex:
            logger.error(f"Fails when try to get a secret: {ex}")
            return {}
        data = response.get("data", {})
        return data.get("data", {})

    def set_kv_secret(self, area: str, context: str, data: dict) -> None:
        self.client.secrets.kv.v2.create_or_update_secret(
            mount_point=area,
            path=context,
            secret=data,
        )
        return None

    def create_userpass(
        self, username: str, password: str, policies: list[str]
    ) -> None:
        userpass_created = self.client.auth.userpass.create_or_update_user(
            username=username,
            password=password,
            policies=policies,
        )
        logger.info(
            f"userpass {username} created: {userpass_created.status_code == 204}"
        )

    def create_policy(self, area: str, service: dict):
        """
        hcl example
        path "dev/*" {
            capabilities = ["read", "list"]
        }
        path "dev/postgres/*" {
            capabilities = ["read", "list"]
        }
        path "sys/mounts/" {
            capabilities = ["read", "list"]
        }
        """
        self.client.sys.create_or_update_policy(
            name=area,
            policy=service,
        )

    def __start(
        self, root_token: str | None, unseal_keys: tuple[str, ...] | None, update: bool
    ) -> dict[str, str | tuple[str, ...] | None]:
        if root_token:
            self.__root_token = root_token
        if unseal_keys:
            self.__unseal_keys = unseal_keys

        logger.info("Starting vault-master . . . .")

        try:
            logger.info(
                f"Statuses: initialized:"
                f' {self.client.seal_status.get("initialized")}'
                f' | sealed: {self.client.seal_status.get("sealed")}'
            )
        except InvalidSchema:
            logger.error("No connection to vault!")
            raise ConnectionError(f"No connection to vault: {self.url}")

        # first start
        if not self.client.seal_status.get("initialized"):
            self.__init()
            self.__unseal()
            self.__init_config()

        # if init (need root token and unsealed keys from input)
        elif self.client.seal_status.get("sealed"):
            self.__unseal()

        self.client = hvac.Client(url=self.url, token=self.__root_token)

        if update:
            logger.info(f"Updating config: {update}")
            self.__init_config()

        logger.info(
            f"Client authenticated (master token): {self.client.is_authenticated()}"
        )

        return {
            "root_token": self.__root_token,
            "unseal_keys": self.__unseal_keys,
        }
