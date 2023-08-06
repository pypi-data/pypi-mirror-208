from typing import Optional

from imagination import container

from dnastack.alpha.client.ewes.client import EWesClient
from dnastack.alpha.client.workflow.client import WorkflowClient
from dnastack.cli.config.context import ContextCommandHandler
from dnastack.cli.helpers.client_factory import ConfigurationBasedClientFactory

WORKBENCH_HOSTNAME = "workbench.dnastack.com"
def _populate_workbench_endpoint():
    handler: ContextCommandHandler = container.get(ContextCommandHandler)
    handler.use(WORKBENCH_HOSTNAME, context_name="workbench", no_auth=False)


def _get_workflow_client(context_name: Optional[str] = None,
                         endpoint_id: Optional[str] = None,
                         namespace: Optional[str] = None) -> WorkflowClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(WorkflowClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(WorkflowClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)


def _get_ewes_client(context_name: Optional[str] = None,
                     endpoint_id: Optional[str] = None,
                     namespace: Optional[str] = None) -> EWesClient:
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)
    try:
        return factory.get(EWesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)
    except AssertionError:
        _populate_workbench_endpoint()
        return factory.get(EWesClient, endpoint_id=endpoint_id, context_name=context_name, namespace=namespace)


class UnableToMergeJsonError(RuntimeError):
    def __init__(self, key):
        super().__init__(f'Unable to merge key {key}. The value for {key} must be of type dict, str, int or float')
