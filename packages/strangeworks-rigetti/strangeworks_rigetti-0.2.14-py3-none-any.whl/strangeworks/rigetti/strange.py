import base64
import pickle
from typing import List, Optional

from pyquil.api._qam import QAMExecutionResult
from qcs_api_client.client import QCSClientConfiguration
from strangeworks.core.client.resource import Product, Resource

import strangeworks

from .qc import QuantumComputer
from .result import StrangeworksExecutionResult


def list_quantum_computers() -> List[str]:
    backends = strangeworks.backends(product_slugs=["rigetti"])
    return backends


def get_qc(
    name: str,
    resource_slug: str,
    as_qvm: Optional[bool] = None,
    noisy: Optional[bool] = None,
    compiler_timeout: float = 10.0,
    execution_timeout: float = 10.0,
    client_configuration: Optional[QCSClientConfiguration] = None,
) -> QuantumComputer:
    # TODO: get_backend asks for a slug not name, so for now we do this:
    ogc = strangeworks.client.get_backends()
    my_backend = None
    for b in ogc:
        if name == "WavefunctionSimulator":
            my_backend = b
            break
        if b.remote_backend_id == name:
            my_backend = b
            break

    if my_backend is not None:
        my_backend.qam = StrangeworksExecutionResult()
        my_backend.compiler = None

    product = Product(slug="rigetti")
    resource = Resource(slug=resource_slug, product=product)

    return QuantumComputer(my_backend, res=resource, as_qvm=as_qvm)


def execution_from_result(response: dict) -> QAMExecutionResult:
    pickled_res = response["pickled_result"]
    pickle_bytes = base64.b64decode(pickled_res)
    return pickle.loads(pickle_bytes)
