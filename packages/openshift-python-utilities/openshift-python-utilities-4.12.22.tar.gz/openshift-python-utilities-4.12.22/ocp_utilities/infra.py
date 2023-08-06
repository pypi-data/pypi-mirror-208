import importlib
import json

import kubernetes
from ocp_resources.node import Node
from ocp_wrapper_data_collector.data_collector import (
    get_data_collector_base_dir,
    get_data_collector_dict,
)
from urllib3.exceptions import MaxRetryError

from ocp_utilities.exceptions import (
    NodeNotReadyError,
    NodesNotHealthyConditionError,
    NodeUnschedulableError,
    PodsFailedOrPendingError,
)
from ocp_utilities.logger import get_logger


LOGGER = get_logger(name=__name__)


def get_client(config_file=None, config_dict=None, context=None, **kwargs):
    """
    Get a kubernetes client.

    Pass either config_file or config_dict.
    If none of them are passed, client will be created from default OS kubeconfig
    (environment variable or .kube folder).

    Args:
        config_file (str): path to a kubeconfig file.
        config_dict (dict): dict with kubeconfig configuration.
        context (str): name of the context to use.

    Returns:
        DynamicClient: a kubernetes client.
    """
    # Ref: https://github.com/kubernetes-client/python/blob/v26.1.0/kubernetes/base/config/kube_config.py
    if config_dict:
        return kubernetes.dynamic.DynamicClient(
            client=kubernetes.config.new_client_from_config_dict(
                config_dict=config_dict, context=context, **kwargs
            )
        )
    try:
        # Ref: https://github.com/kubernetes-client/python/blob/v26.1.0/kubernetes/base/config/__init__.py
        LOGGER.info("Trying to get client via new_client_from_config")
        return kubernetes.dynamic.DynamicClient(
            client=kubernetes.config.new_client_from_config(
                config_file=config_file, context=context, **kwargs
            )
        )
    except MaxRetryError:
        # Ref: https://github.com/kubernetes-client/python/blob/v26.1.0/kubernetes/base/config/incluster_config.py
        LOGGER.info("Trying to get client via incluster_config")
        return kubernetes.dynamic.DynamicClient(
            client=kubernetes.config.incluster_config.load_incluster_config(
                client_configuration=kwargs.get("client_configuration"),
                try_refresh_token=kwargs.get("try_refresh_token", True),
            )
        )


def assert_nodes_ready(nodes):
    """
    Validates all nodes are in ready

    Args:
         nodes(list): List of Node objects

    Raises:
        NodeNotReadyError: Assert on node(s) in not ready state
    """
    LOGGER.info("Verify all nodes are ready.")
    not_ready_nodes = [node.name for node in nodes if not node.kubelet_ready]
    if not_ready_nodes:
        raise NodeNotReadyError(
            f"Following nodes are not in ready state: {not_ready_nodes}"
        )


def assert_nodes_schedulable(nodes):
    """
    Validates all nodes are in schedulable state

    Args:
         nodes(list): List of Node objects

    Raises:
        NodeUnschedulableError: Asserts on node(s) not schedulable
    """
    LOGGER.info("Verify all nodes are schedulable.")
    unschedulable_nodes = [
        node.name for node in nodes if node.instance.spec.unschedulable
    ]
    if unschedulable_nodes:
        raise NodeUnschedulableError(
            f"Following nodes are in unscheduled state: {unschedulable_nodes}"
        )


def assert_pods_failed_or_pending(pods):
    """
    Validates all pods are not in failed nor pending phase

    Args:
         pods: List of pod objects

    Raises:
        PodsFailedOrPendingError: if there are failed or pending pods
    """
    LOGGER.info("Verify all pods are not failed nor pending.")

    failed_or_pending_pods = []
    for pod in pods:
        if pod.exists:
            pod_status = pod.instance.status.phase
            if pod_status in [pod.Status.PENDING, pod.Status.FAILED]:
                failed_or_pending_pods.append(
                    f"name: {pod.name}, namespace: {pod.namespace}, status: {pod_status}\n"
                )

    if failed_or_pending_pods:
        failed_or_pending_pods_str = "\t".join(map(str, failed_or_pending_pods))
        raise PodsFailedOrPendingError(
            f"The following pods are failed or pending:\n\t{failed_or_pending_pods_str}",
        )


def assert_nodes_in_healthy_condition(
    nodes,
    healthy_node_condition_type=None,
):
    """
    Validates nodes are in a healthy condition.
    Nodes Ready condition is True and the following node conditions are False:
        - DiskPressure
        - MemoryPressure
        - PIDPressure
        - NetworkUnavailable
        - OutOfDisk

    Args:
         nodes(list): List of Node objects

         healthy_node_condition_type (dict):
            Dictionary with condition type and the respective healthy condition
                status: Example: {"DiskPressure": "False", ...}

    Raises:
        NodesNotHealthyConditionError: if any nodes DiskPressure MemoryPressure,
            PIDPressure, NetworkUnavailable, etc condition is True
    """
    LOGGER.info("Verify all nodes are in a healthy condition.")

    if not healthy_node_condition_type:
        healthy_node_condition_type = {
            "OutOfDisk": Node.Condition.Status.FALSE,
            "DiskPressure": Node.Condition.Status.FALSE,
            "MemoryPressure": Node.Condition.Status.FALSE,
            "NetworkUnavailable": Node.Condition.Status.FALSE,
            "PIDPressure": Node.Condition.Status.FALSE,
            Node.Condition.READY: Node.Condition.Status.TRUE,
        }

    if not isinstance(healthy_node_condition_type, dict):
        raise TypeError(
            f"A dict is required but got type {type(healthy_node_condition_type)}"
        )

    unhealthy_nodes_with_conditions = {}
    for node in nodes:
        unhealthy_condition_type_list = [
            condition.type
            for condition in node.instance.status.conditions
            if condition.type in healthy_node_condition_type
            and healthy_node_condition_type[condition.type] != condition.status
        ]

        if unhealthy_condition_type_list:
            unhealthy_nodes_with_conditions[node.name] = unhealthy_condition_type_list

    if unhealthy_nodes_with_conditions:
        nodes_unhealthy_condition_error_str = json.dumps(
            unhealthy_nodes_with_conditions,
            indent=3,
        )
        raise NodesNotHealthyConditionError(
            f"Following are nodes with unhealthy condition/s:\n{nodes_unhealthy_condition_error_str}"
        )


class DynamicClassCreator:
    """
    Taken from https://stackoverflow.com/a/66815839
    """

    def __init__(self):
        self.created_classes = {}

    def __call__(self, base_class):
        if base_class in self.created_classes:
            return self.created_classes[base_class]

        class BaseResource(base_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def _set_dynamic_class_creator_label(self):
                self.res.setdefault("metadata", {}).setdefault("labels", {}).update(
                    {"created-by-dynamic-class-creator": "Yes"}
                )

            def to_dict(self):
                if not self.res:
                    super().to_dict()

                self._set_dynamic_class_creator_label()

            def clean_up(self):
                try:
                    data_collector_dict = get_data_collector_dict()
                    if data_collector_dict:
                        data_collector_directory = get_data_collector_base_dir(
                            data_collector_dict=data_collector_dict
                        )

                        collect_data_function = data_collector_dict[
                            "collect_data_function"
                        ]
                        module_name, function_name = collect_data_function.rsplit(
                            ".", 1
                        )
                        import_module = importlib.import_module(name=module_name)
                        collect_data_function = getattr(import_module, function_name)
                        LOGGER.info(
                            f"[Data collector] Collecting data for {self.kind} {self.name}"
                        )
                        collect_data_function(
                            directory=data_collector_directory,
                            resource_object=self,
                            collect_pod_logs=data_collector_dict.get(
                                "collect_pod_logs", False
                            ),
                        )
                except Exception as exception_:
                    LOGGER.warning(
                        f"[Data collector] failed to collect data for {self.kind} {self.name}\n"
                        f"exception: {exception_}"
                    )
                super().clean_up()

        self.created_classes[base_class] = BaseResource
        return BaseResource


def cluster_resource(base_class):
    """
    Base class for all resources in order to override clean_up() method to collect resource data.
    data_collect_yaml dict can be set via py_config pytest plugin or via
    environment variable OPENSHIFT_PYTHON_WRAPPER_DATA_COLLECTOR_YAML.

    YAML format:
        data_collector_base_directory: "<base directory for data collection>"
        collect_data_function: "<import path for data collection method>"

    YAML Example:
        data_collector_base_directory: "tests-collected-info"
        collect_data_function: "utilities.data_collector.collect_data"

    Args:
        base_class (Class): Resource class to be used.

    Returns:
        Class: Resource class.

    Example:
        name = "container-disk-vm"
        with cluster_resource(VirtualMachineForTests)(
            namespace=namespace.name,
            name=name,
            client=unprivileged_client,
            body=fedora_vm_body(name=name),
        ) as vm:
            running_vm(vm=vm)
    """
    creator = DynamicClassCreator()
    return creator(base_class=base_class)
