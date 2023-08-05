import json
from typing import Optional

import dimod
import networkx as nx
import numpy as np
import qiskit
import strangeworks
from strangeworks.core.errors.error import StrangeworksError

import strangeworks_qaoa.utils as utils


class StrangeworksQAOA:
    """Strangeworks client object."""

    def __init__(self, resource_slug: Optional[str] = " ") -> None:
        if resource_slug != " " and resource_slug != "":
            self.rsc = strangeworks.resources(slug=resource_slug)[0]
        else:
            rsc_list = strangeworks.resources()
            for rr in range(len(rsc_list)):
                if rsc_list[rr].product.slug == "qaoa":
                    self.rsc = rsc_list[rr]

        self.backend_list = " "

    def backends(self):
        """
        To-Do: Add cross check as to which backends the current user actually has
          access to.
                Currently, this just lists all backends that could work with the qaoa
                  service.
        """

        all_backends = strangeworks.backends(backend_type_slugs=["sw-qaoa"])

        aws_backends = []
        aws_sim_backends = []
        ibmq_backends = []
        ibm_cloud_backends = []
        ibm_sim_backends = []
        for bb in range(len(all_backends)):
            try:
                arn_str = all_backends[bb].remote_backend_id[0:3]
                # print(arn_str)
                if arn_str == "arn" and all_backends[bb].remote_status != "retired":
                    if (
                        all_backends[bb].name == "SV1"
                        or all_backends[bb].name == "TN1"
                        or all_backends[bb].name == "dm1"
                    ):
                        backend_temp = {
                            "name": all_backends[bb].name,
                            "provider": "AWS_Simulator",
                            "remote_status": all_backends[bb].remote_status,
                            "arn": all_backends[bb].remote_backend_id,
                        }
                        aws_sim_backends.append(backend_temp)
                    else:
                        backend_temp = {
                            "name": all_backends[bb].name,
                            "provider": "AWS",
                            "remote_status": all_backends[bb].remote_status,
                            "arn": all_backends[bb].remote_backend_id,
                        }
                        aws_backends.append(backend_temp)
            except AttributeError:
                None

            try:
                ibm_str = all_backends[bb].name[0:3]
                id_str = all_backends[bb].remote_backend_id[0:3]
                if ibm_str == "ibm":
                    if id_str == "ibm":
                        prov = "IBM_Cloud"
                        backend_temp = {
                            "backend_name": all_backends[bb].name,
                            "provider": prov,
                            "remote_status": all_backends[bb].remote_status,
                        }
                        ibm_cloud_backends.append(backend_temp)
                    else:
                        if all_backends[bb].name == "ibmq_qasm_simulator":
                            prov = "IBM_Simulator"
                            backend_temp = {
                                "backend_name": all_backends[bb].name,
                                "provider": prov,
                                "remote_status": all_backends[bb].remote_status,
                            }
                            ibm_sim_backends.append(backend_temp)
                        else:
                            prov = "IBMQ"
                            backend_temp = {
                                "backend_name": all_backends[bb].name,
                                "provider": prov,
                                "remote_status": all_backends[bb].remote_status,
                            }
                            ibmq_backends.append(backend_temp)
                elif ibm_str == "sim":
                    prov = "IBM_Simulator"
                    backend_temp = {
                        "backend_name": all_backends[bb].name,
                        "provider": prov,
                        "remote_status": all_backends[bb].remote_status,
                    }
                    ibm_sim_backends.append(backend_temp)
            except AttributeError:
                None

        self.backend_list = {
            "AWS": aws_backends,
            "AWS_Sim": aws_sim_backends,
            "IBMQ": ibmq_backends,
            "IBM_Cloud": ibm_cloud_backends,
            "IBM_Sim": ibm_sim_backends,
        }

        return self.backend_list

    def run(self, backend, problem, problem_params):
        """
        Method to submit QAOA problem to backend.

        Parameters:
            problem:
                Hamiltonian whose ground state we want to find.
                Can be either a networkx graph, a qiskit PauliSumOp operator, a QUBO
                Matrix or a Dwave BinaryQuadraticModel.
            problem_params:
                nqubits (int): number of qubits
                shotsin (int): number of shots. Number of times quantum circuit is run
                                and measured
                maxiter (int): max number of iteration loops in minimisation
                p (int): Optional. Number of repetitions in qaoa ansatz
                alpha (float): Optional. Parameter between 0 and 1, which controls the
                                CVar expectation value,
                                - https://arxiv.org/pdf/1907.04769.pdf
                                alpha = 1, usual expectation value
                                alpha < 1, modified expectation value for quantum
                                simulation with classical outputs
                theta0 (array): Optional, initial vector of parameters.
                optimizer (str): Optional, string specifying classical optimizer,
                                default='SPSA'.
                ansatz (str or QuantumCircuit): Optional, Variational circuit
                                                parametrized with coefficients to
                                                optimise for the energy
                ising (bool): Optional, If True then the input problem is treated as
                                    an Ising problem. If False or unspecified, then the
                                    input problem is treated as a QUBO problem.
                problem_type (str): Optional, If the problem is a quantum encoding of a
                classical problem (i.e. the solution is one of the basis states)
                                    then we can make some simplifications and employ
                                    some tricks to make the algorithm potentially more
                                    optimal.
                optimization_level: IBM only. How much optimization to perform on the
                                    circuits.
                                    Higher levels generate more optimized circuits,
                                    at the expense of longer transpilation times. This
                                    is based on the ``optimization_level`` parameter in
                                    qiskit-terra but may include backend-specific
                                    optimization. Default: 1.

                                    * 0: no optimization
                                    * 1: light optimization
                                    * 2: heavy optimization
                                    * 3: even heavier optimization

                resilience_level: IBM only. How much resilience to build against errors.
                                    Higher levels generate more accurate results,
                                    at the expense of longer processing times. Default:
                                    1.

                                    * 0: No mitigation.
                                    * 1: Minimal mitigation costs. Mitigate error
                                    associated with readout errors.
                                    * 2: Medium mitigation costs. Typically reduces
                                    bias in estimators but is not guaranteed to be zero
                                    bias. Only applies to estimator.
                                    * 3: Heavy mitigation with layer sampling.
                                    Theoretically expected to deliver zero bias
                                    estimators. Only applies to estimator.

        Returns:
            Strangeworks Job object
        """

        if self.backend_list == " ":
            self.backends()

        aws = False
        ibm = False
        for nn in range(len(self.backend_list["AWS"])):
            if self.backend_list["AWS"][nn]["name"] == backend:
                aws = True
                backend_id = self.backend_list["AWS"][nn]["arn"]

        for nn in range(len(self.backend_list["IBMQ"])):
            if self.backend_list["IBMQ"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_quantum"
                backend_id = self.backend_list["IBMQ"][nn]["backend_name"]

        for nn in range(len(self.backend_list["IBM_Cloud"])):
            if self.backend_list["IBM_Cloud"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_cloud"
                backend_id = self.backend_list["IBM_Cloud"][nn]["backend_name"]

        for nn in range(len(self.backend_list["AWS_Sim"])):
            if self.backend_list["AWS_Sim"][nn]["name"] == backend:
                aws = True
                backend_id = self.backend_list["AWS_Sim"][nn]["arn"]

        for nn in range(len(self.backend_list["IBM_Sim"])):
            if self.backend_list["IBM_Sim"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_quantum"
                backend_id = self.backend_list["IBM_Sim"][nn]["backend_name"]

        if ibm is False and aws is False:
            raise StrangeworksError("Unable to Find Backend")

        # Check which format the problem is specified in and convert to the form which
        # our QUBO solver can accept.
        if type(problem) == nx.classes.graph.Graph:
            H = utils.get_Ham_from_graph(problem)
        elif type(problem) == qiskit.opflow.primitive_ops.pauli_sum_op.PauliSumOp:
            H = utils.get_Ham_from_PauliSumOp(problem)
        elif type(problem) == np.ndarray:
            H = utils.get_Ham_from_QUBO(problem)
        elif (
            type(problem) == dict
            and problem.get("BQM") is not None
            and type(problem.get("BQM"))
            == dimod.binary.binary_quadratic_model.BinaryQuadraticModel
        ):
            QUBO = problem["BQM"].to_numpy_matrix(
                variable_order=problem.get("variable_order")
            )
            H = utils.get_Ham_from_QUBO(QUBO)
        else:
            raise StrangeworksError("Problem not in currently supported format")

        problem_params["H"] = json.dumps(H)
        problem_params["ising"] = (
            json.dumps(problem_params["ising"])
            if problem_params.get("ising")
            else json.dumps(False)
        )
        problem_params["warm_start"] = (
            json.dumps(problem_params["warm_start"])
            if problem_params.get("warm_start")
            else json.dumps(False)
        )

        if aws is True:
            input_params = {
                "provider": "aws",
                "backend": backend_id,
                "hyperparams": json.dumps(problem_params),
            }
        elif ibm is True:
            input_params = {
                "provider": "ibm",
                "channel": channel,
                "backend": backend_id,
                "hyperparams": json.dumps(problem_params),
            }

        sw_job = strangeworks.execute(self.rsc, input_params, "run_hybrid_job")

        return sw_job

    def update_status(self, sw_job):
        if type(sw_job) is dict:
            job_slug = sw_job.get("slug")
        else:
            job_slug = sw_job.slug

        status = strangeworks.execute(
            self.rsc, {"payload": {"job_slug": job_slug}}, "status"
        )

        return status

    def get_results(self, sw_job, calculate_exact_sol=False, display_results=False):
        if type(sw_job) is dict:
            job_slug = sw_job.get("slug")
        else:
            job_slug = sw_job.slug

        result_url = strangeworks.execute(
            self.rsc, {"payload": {"job_slug": job_slug}}, "get_results_url"
        )

        if result_url:
            result_file = strangeworks.download_job_files([result_url])[0]
        else:
            """
            If results file is not there, run the function to produce the results file
            and plots for the platform
            """
            result = strangeworks.execute(
                self.rsc, {"payload": {"job_slug": job_slug}}, "result"
            )

            if result.strip().upper() == "COMPLETED":
                result_url = strangeworks.execute(
                    self.rsc, {"payload": {"job_slug": job_slug}}, "get_results_url"
                )
                if result_url:
                    result_file = strangeworks.download_job_files([result_url])[0]
                else:
                    raise StrangeworksError(f"unable to open {result_url}")
            else:
                return result

        if calculate_exact_sol:
            inputs_url = strangeworks.execute(
                self.rsc, {"payload": {"job_slug": job_slug}}, "get_inputs_url"
            )
            inputs = strangeworks.download_job_files([inputs_url])[0]

            H = json.loads(inputs["H"])
            nqubits = int(inputs["nqubits"])

            try:
                En_exact = utils.get_exact_en(
                    utils.get_graph_from_Ham(H, nqubits),
                    nqubits,
                    ising=json.loads(inputs["ising"]) if inputs.get("ising") else False,
                )
            except Exception:
                En_exact = "!!problem too big for exact solution!!"
            result_file["En_exact"] = En_exact
        else:
            result_file["En_exact"] = None

        if display_results:
            sol = result_file["sol"]
            En_exact = result_file["En_exact"]
            En_sol = result_file["en_min"]
            En_av = result_file["en"][len(result_file["en"]) - 1]

            print(
                f"The average energy (expectation value) of the final state is {En_av}"
            )
            print(f"The solution found by the algorithm is: {sol}")
            print(f"The energy of the solution found by the algorithm is {En_sol}")
            print(f"The exact optimal energy is {En_exact}")

        return result_file

    def job_list(self, update_status=True):
        job_list = strangeworks.jobs()

        qaoa_job_list = []
        for jj in range(len(job_list)):
            if job_list[jj].resource.product.slug == "qaoa":
                if job_list[jj].external_identifier[0:3] == "arn":
                    prov = "AWS"
                else:
                    prov = "IBM"

                if job_list[jj].status != "COMPLETED" and update_status is True:
                    try:
                        status = strangeworks.execute(
                            self.rsc,
                            {"payload": {"job_slug": job_list[jj].slug}},
                            "status",
                        )
                    except Exception:
                        status = job_list[jj].status
                else:
                    status = job_list[jj].status

                temp = {
                    "slug": job_list[jj].slug,
                    "Status": status,
                    "Provider": prov,
                    "resource_slug": job_list[jj].resource.slug,
                }
                qaoa_job_list.append(temp)

        return qaoa_job_list
