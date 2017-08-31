from typing import Generator, Union, Iterable

import libzfs

import libiocage.lib.Jail
import libiocage.lib.JailFilter
import libiocage.lib.helpers


class JailsGenerator(list):
    # Keys that are stored on the Jail object, not the configuration
    JAIL_KEYS = [
        "jid",
        "name",
        "running",
        "ip4.addr",
        "ip6.addr"
    ]

    def __init__(self,
                 filters=None,
                 host=None,
                 logger=None,
                 zfs=None):

        libiocage.lib.helpers.init_logger(self, logger)
        libiocage.lib.helpers.init_zfs(self, zfs)
        libiocage.lib.helpers.init_host(self, host)
        self.zfs = libzfs.ZFS(history=True, history_prefix="<iocage>")

        self._filters = None
        self.filters = filters
        list.__init__(self, [])

    def __iter__(self):

        for jail_dataset in self.jail_datasets:

            jail_name = self._get_name_from_jail_dataset(jail_dataset)
            if self._filters.match_key("name", jail_name) is not True:
                # Skip all jails that do not even match the name
                continue

            # ToDo: Do not load jail if filters do not require to
            jail = self._load_jail_from_dataset(jail_dataset)
            if self._filters.match_jail(jail):
                yield jail

    def _create_jail(self, *args, **kwargs):
        kwargs["logger"] = self.logger
        kwargs["host"] = self.host
        kwargs["zfs"] = self.zfs
        return libiocage.lib.Jail.Jail(*args, **kwargs)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(
        self,
        value: Union[
            str,
            Iterable[Union[libiocage.lib.JailFilter.Terms, str]]
        ]
    ):

        if isinstance(value, libiocage.lib.JailFilter.Terms):
            self._filters = value
        else:
            self._filters = libiocage.lib.JailFilter.Terms(value)

    @property
    def jail_datasets(self) -> list:
        jails_dataset = self.host.datasets.jails
        return list(jails_dataset.children)

    def _load_jail_from_dataset(
        self,
        dataset: libzfs.ZFSDataset
    ) -> Generator[libiocage.lib.Jail.JailGenerator, None, None]:

        return self._create_jail({
            "name": self._get_name_from_jail_dataset(dataset)
        })

    def _get_name_from_jail_dataset(
        self,
        dataset: libzfs.ZFSDataset
    ) -> str:

        return dataset.name.split("/").pop()


class Jails(JailsGenerator):

    def _create_jail(self, *args, **kwargs):
        kwargs["logger"] = self.logger
        kwargs["host"] = self.host
        kwargs["zfs"] = self.zfs
        return libiocage.lib.Jail.Jail(*args, **kwargs)

    def __iter__(self):
        return list(JailsGenerator.__iter__(self))
