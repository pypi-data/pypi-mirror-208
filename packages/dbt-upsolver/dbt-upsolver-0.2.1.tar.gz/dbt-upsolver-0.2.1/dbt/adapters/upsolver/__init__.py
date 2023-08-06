from dbt.adapters.upsolver.connections import UpsolverConnectionManager # noqa
from dbt.adapters.upsolver.connections import UpsolverCredentials
from dbt.adapters.upsolver.impl import UpsolverAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import upsolver


Plugin = AdapterPlugin(
    adapter=UpsolverAdapter,
    credentials=UpsolverCredentials,
    include_path=upsolver.PACKAGE_PATH
    )
