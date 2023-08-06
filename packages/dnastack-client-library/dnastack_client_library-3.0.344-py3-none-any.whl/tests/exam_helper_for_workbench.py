import json
from typing import List, Optional
from urllib.parse import urljoin

from imagination import container
from pydantic import BaseModel

from dnastack import use, ServiceEndpoint
from dnastack.client.workbench.ewes.client import EWesClient
from dnastack.client.workbench.ewes.models import MinimalExtendedRun, ExtendedRunRequest, BatchRunResponse, BatchRunRequest
from dnastack.client.factory import EndpointRepository
from dnastack.common.environments import env
from dnastack.context.manager import ContextManager
from dnastack.http.session import HttpSession
from tests.exam_helper import WithTestUserTestCase
from tests.wallet_hellper import TestUser, Policy, Statement, Principal, Resource


class EngineOAuthConfig(BaseModel):
    clientId: str
    clientSecret: str
    tokenUri: str
    resource: str
    scope: str


class EngineAdapterConfiguration(BaseModel):
    type: str
    url: str
    oauth_config: Optional[EngineOAuthConfig]


class ExecutionEngine(BaseModel):
    id: Optional[str]
    version: Optional[str]
    name: str
    provider: str
    region: str
    default: bool
    engine_adapter_configuration: EngineAdapterConfiguration


class BaseWorkbenchTestCase(WithTestUserTestCase):
    workbench_base_url = env('E2E_WORKBENCH_BASE_URL', required=False, default='http://localhost:9191')
    ewes_service_base_url = env('E2E_EWES_SERVICE_BASE_URL', required=False, default='http://localhost:9095')
    workflow_service_base_url = env('E2E_WORKFLOW_SERVICE_BASE_URL', required=False, default='http://localhost:9192')
    execution_engine: ExecutionEngine = ExecutionEngine(
        **json.loads(env('E2E_WORKBENCH_EXECUTION_ENGINE_JSON',
                         required=False,
                         default=ExecutionEngine(
                             name='Cromwell on Local',
                             provider='LOCAL',
                             region='local',
                             default=True,
                             engine_adapter_configuration=EngineAdapterConfiguration(
                                 type='WES_ON_CROMWELL',
                                 url='http://localhost:8090',
                                 oauth_config=EngineOAuthConfig(
                                     clientId='ewes-service',
                                     clientSecret='dev-secret-never-use-in-prod',
                                     tokenUri='http://localhost:8081/oauth/token',
                                     resource='http://localhost:8090/',
                                     scope='wes'
                                 )
                             )
                         ).json())))
    namespace: str = None

    @classmethod
    def get_factory(cls) -> EndpointRepository:
        return cls.get_context_manager().use(cls.get_context_urls()[0], no_auth=True)

    @classmethod
    def get_context_urls(cls) -> List[str]:
        return [f'{cls.workbench_base_url}/api/service-registry']

    @classmethod
    def get_app_url(cls) -> str:
        return cls.workbench_base_url

    @classmethod
    def get_access_policy(cls, test_user: TestUser) -> Policy:
        return Policy(
            id=f'{cls.test_policy_prefix}-{test_user.id}',
            statements=[Statement(
                actions=['workbench:ui'],
                principals=[Principal(
                    email=f'{test_user.email}',
                    type='user'
                )],
                resources=[Resource(
                    uri=f'{cls.workbench_base_url}/{test_user.id}/'
                )]
            )],
            tags=['test', 'dnastack-client-library', 'workbench']
        )

    @classmethod
    def do_on_setup_class_before_auth(cls) -> None:
        super().do_on_setup_class_before_auth()
        cls.namespace = cls.test_user.id

        with cls._wallet_helper.login_to_app(cls.workbench_base_url,
                                             cls.test_user.email,
                                             cls.test_user.personalAccessToken) as session:
            cls.execution_engine = cls._create_execution_engine(session)
            cls._base_logger.info(f'Class {cls.__name__}: Created execution engine: {cls.execution_engine}')

    @classmethod
    def do_on_teardown_class(cls) -> None:
        with cls._wallet_helper.login_to_app(cls.workbench_base_url,
                                             cls.test_user.email,
                                             cls.test_user.personalAccessToken) as session:
            cls._base_logger.info(f'Class {cls.__name__}: Cleaning up namespace: {cls.namespace}')
            cls._cleanup_namespace(session)

        # Delete test user and policy as last
        super().do_on_teardown_class()

    @classmethod
    def _get_ewes_service_endpoints(cls) -> List[ServiceEndpoint]:
        # noinspection PyUnresolvedReferences
        factory: EndpointRepository = cls.get_factory()

        return [
            endpoint
            for endpoint in factory.all()
            if endpoint.type in EWesClient.get_supported_service_types()
        ]

    @classmethod
    def get_ewes_client(cls, index: int = 0) -> Optional[EWesClient]:
        compatible_endpoints = cls._get_ewes_service_endpoints()

        if not compatible_endpoints:
            raise RuntimeError('No ewes-service compatible endpoints for this test')

        if index >= len(compatible_endpoints):
            raise RuntimeError(f'Requested ewes-service compatible endpoint #{index} but it does not exist.')

        compatible_endpoint = compatible_endpoints[index]

        return EWesClient.make(compatible_endpoint, cls.namespace)

    @classmethod
    def _create_execution_engine(cls, session: HttpSession) -> ExecutionEngine:
        response = session.post(urljoin(cls.workbench_base_url, f'/services/ewes-service/{cls.namespace}/engines'),
                                json=cls.execution_engine.dict())
        return ExecutionEngine(**response.json())

    @classmethod
    def _cleanup_namespace(cls, session: HttpSession) -> None:
        access_token = cls._wallet_helper.get_access_token(f'{cls.ewes_service_base_url}/', 'namespace')
        session.delete(urljoin(cls.ewes_service_base_url, cls.namespace),
                       headers={'Authorization': f'Bearer {access_token}'})
        access_token = cls._wallet_helper.get_access_token(f'{cls.workflow_service_base_url}/', 'namespace')
        session.delete(urljoin(cls.workflow_service_base_url, cls.namespace),
                       headers={'Authorization': f'Bearer {access_token}'})

    def submit_hello_world_workflow_run(self) -> MinimalExtendedRun:
        ewes_client: EWesClient = self.get_ewes_client()
        return ewes_client.submit_run(ExtendedRunRequest(
            workflow_url='vrockai:dockstore-whalesay/dnastack',
            workflow_type='WDL',
            workflow_type_version='draft-2',
            workflow_params={
                'test.hello.name': 'foo'
            }
        ))

    def submit_hello_world_workflow_batch(self) -> BatchRunResponse:
        ewes_client: EWesClient = self.get_ewes_client()
        return ewes_client.submit_batch(BatchRunRequest(
            workflow_url='vrockai:dockstore-whalesay/dnastack',
            workflow_type='WDL',
            workflow_type_version='draft-2',
            run_requests=[
                ExtendedRunRequest(
                    workflow_params={
                        'test.hello.name': 'foo'
                    }
                ),
                ExtendedRunRequest(
                    workflow_params={
                        'test.hello.name': 'bar'
                    }
                )
            ]
        ))
