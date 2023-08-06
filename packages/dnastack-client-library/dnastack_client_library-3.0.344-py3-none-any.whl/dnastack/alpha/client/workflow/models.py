from enum import Enum
from typing import Dict, Optional, Any, List

from pydantic import BaseModel


class WorkflowDescriptor(BaseModel):
    workflow_name: str
    input_schema: Dict
    output_schema: Dict
    wdl_version: str
    errors: Optional[Any]


class WorkflowVersion(BaseModel):
    workflowId: Optional[str]
    id: str
    externalId: Optional[str]
    versionName: str
    workflowName: str
    createdAt: Optional[str]
    lastUpdatedAt: Optional[str]
    descriptorType: str
    authors: Optional[List[str]]
    description: Optional[str]
    deleted: Optional[bool]
    etag: Optional[str]


class Workflow(BaseModel):
    internalId: str
    source: str
    name: str
    description: Optional[str]
    lastUpdatedAt: Optional[str]
    latestVersion: str
    authors: Optional[List[str]]
    versions: Optional[List[WorkflowVersion]]
    deleted: Optional[bool]
    etag: Optional[str]


class WorkflowFileType(str, Enum):
    primary = "PRIMARY_DESCRIPTOR"
    secondary = "DESCRIPTOR"
    test_file = "TEST_FILE"
    other = "OTHER"

class WorkflowSource(str,Enum):
    dockstore = "DOCKSTORE"
    custom = "CUSTOM"

class WorkflowFile(BaseModel):
    path: str
    file_type: WorkflowFileType
    content: Optional[str]
    file_url: Optional[str]


class WorkflowCreate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    versionName: Optional[str]
    files: List[WorkflowFile]


class WorkflowVersionCreate(BaseModel):
    versionName: str
    descriptions: Optional[str]
    files: List[WorkflowFile]


class WorkflowListResult(BaseModel):
    workflows: List[Workflow]


class WorkflowVersionListResult(BaseModel):
    versions: List[WorkflowVersion]

