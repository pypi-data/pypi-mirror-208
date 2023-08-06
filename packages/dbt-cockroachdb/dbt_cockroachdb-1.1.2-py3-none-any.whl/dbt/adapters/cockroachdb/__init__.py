from dbt.adapters.cockroachdb.connections import cockroachdbConnectionManager # noqa
from dbt.adapters.cockroachdb.connections import cockroachdbCredentials
from dbt.adapters.cockroachdb.impl import cockroachdbAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import cockroachdb


Plugin = AdapterPlugin(
    adapter=cockroachdbAdapter,
    credentials=cockroachdbCredentials,
    include_path=cockroachdb.PACKAGE_PATH
    )
