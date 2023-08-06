# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ibis_substrait',
 'ibis_substrait.compiler',
 'ibis_substrait.extensions',
 'ibis_substrait.proto',
 'ibis_substrait.proto.substrait',
 'ibis_substrait.proto.substrait.ibis',
 'ibis_substrait.proto.substrait.ibis.extensions',
 'ibis_substrait.tests',
 'ibis_substrait.tests.compiler',
 'ibis_substrait.tests.integration']

package_data = \
{'': ['*'],
 'ibis_substrait.tests.compiler': ['snapshots/test_tpch/test_compile/tpc_h01/*',
                                   'snapshots/test_tpch/test_compile/tpc_h03/*',
                                   'snapshots/test_tpch/test_compile/tpc_h04/*',
                                   'snapshots/test_tpch/test_compile/tpc_h05/*',
                                   'snapshots/test_tpch/test_compile/tpc_h06/*',
                                   'snapshots/test_tpch/test_compile/tpc_h07/*',
                                   'snapshots/test_tpch/test_compile/tpc_h09/*',
                                   'snapshots/test_tpch/test_compile/tpc_h10/*',
                                   'snapshots/test_tpch/test_compile/tpc_h11/*',
                                   'snapshots/test_tpch/test_compile/tpc_h12/*',
                                   'snapshots/test_tpch/test_compile/tpc_h13/*',
                                   'snapshots/test_tpch/test_compile/tpc_h18/*',
                                   'snapshots/test_tpch/test_compile/tpc_h19/*',
                                   'snapshots/test_tpch/test_compile/tpc_h20/*',
                                   'snapshots/test_tpch/test_compile/tpc_h21/*',
                                   'snapshots/test_tpch/test_compile/tpc_h22/*']}

install_requires = \
['ibis-framework>=3', 'packaging>=21.3', 'protobuf>=3.20.1', 'pyyaml>=5']

setup_kwargs = {
    'name': 'ibis-substrait',
    'version': '2.28.2',
    'description': 'Subtrait compiler for ibis',
    'long_description': '# [Ibis](https://ibis-project.org) + [Substrait](https://substrait.io)\n\nThis repo houses the Substrait compiler for ibis.\n\nWe\'re just getting started here, so stay tuned!\n\n# Usage\n\n```python\n>>> import ibis\n\n>>> t = ibis.table(\n    [("a", "string"), ("b", "float"), ("c", "int32"), ("d", "int64"), ("e", "int64")],\n    "t",\n)\n\n>>> expr = t.group_by(["a", "b"]).aggregate([t.c.sum().name("sum")]).select("b", "sum")\n>>> expr\nr0 := UnboundTable: t\n  a string\n  b float64\n  c int32\n  d int64\n  e int64\n\nr1 := Aggregation[r0]\n  metrics:\n    sum: Sum(r0.c)\n  by:\n    a: r0.a\n    b: r0.b\n\nSelection[r1]\n  selections:\n    b:   r1.b\n    sum: r1.sum\n\n\n>>> ibis.show_sql(expr)\nSELECT\n  t0.b,\n  t0.sum\nFROM (\n  SELECT\n    t1.a AS a,\n    t1.b AS b,\n    SUM(t1.c) AS sum\n  FROM t AS t1\n  GROUP BY\n    t1.a,\n    t1.b\n) AS t0\n\n>>> from ibis_substrait.compiler.core import SubstraitCompiler\n\n>>> compiler = SubstraitCompiler()\n\n>>> proto = compiler.compile(expr)\n```\n',
    'author': 'Ibis Contributors',
    'author_email': 'None',
    'maintainer': 'Ibis Contributors',
    'maintainer_email': 'None',
    'url': 'https://github.com/ibis-project/ibis-substrait',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
