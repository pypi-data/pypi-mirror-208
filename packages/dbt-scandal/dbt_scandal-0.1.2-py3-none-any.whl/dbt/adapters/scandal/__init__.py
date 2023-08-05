from dbt.adapters.base.plugin import AdapterPlugin
from dbt.adapters.scandal.connections import (
    ScandalConnectionManager,  # noqa
    ScandalCredentials,
)
from dbt.adapters.scandal.impl import ScandalAdapter
from dbt.include import scandal

Plugin = AdapterPlugin(
    adapter=ScandalAdapter,  # type:ignore
    credentials=ScandalCredentials,
    include_path=scandal.PACKAGE_PATH,
)
