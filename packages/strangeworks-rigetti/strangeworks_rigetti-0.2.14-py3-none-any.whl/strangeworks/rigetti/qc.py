from pyquil import Program
from pyquil.api import QuantumComputer
from strangeworks.core.client.resource import Resource
from strangeworks.core.errors.error import StrangeworksError

import strangeworks
from strangeworks.rigetti.result import StrangeworksExecutionResult


class QuantumComputer(QuantumComputer):
    def __init__(self, ogc: QuantumComputer, res: Resource, as_qvm: bool):
        self.as_qvm = "True" if as_qvm else "False"
        self.res = res
        super().__init__(
            name=ogc.name,
            qam=ogc.qam,
            compiler=ogc.compiler,
        )

    def run(
        self, program, circuit_type=None, shots: int = 1
    ) -> StrangeworksExecutionResult:
        if isinstance(program, Program):
            payload = self.__serialize_program(program, circuit_type)
            endpoint = "jobs"
        elif isinstance(program, dict):
            payload = program
            payload["circuit_type"] = circuit_type
            endpoint = "kernel"
            self.res.product.slug = "rigetti-kernel-method"

            if "pixels" in program:
                endpoint = "qnn"
                self.res.product.slug = "rigetti-qnn"

        else:
            raise StrangeworksError.invalid_argument(
                "must pass a Program to compile & execute with Rigetti"
            )

        payload["as_qvm"] = self.as_qvm

        results = strangeworks.execute(
            res=self.res,
            payload=payload,
            endpoint=endpoint,
        )

        if isinstance(program, dict):
            return results

        return StrangeworksExecutionResult.from_json(results)

    def __serialize_program(self, p: Program, circuit_type) -> dict:
        d = self.program_to_json(p)
        d["as_qvm"] = self.as_qvm
        d["circuit_type"] = circuit_type
        return d

    def program_to_json(self, prg: Program) -> dict:
        return {
            "target": self.name,
            "circuit": prg.out(),
            "shots": prg.num_shots,
        }
