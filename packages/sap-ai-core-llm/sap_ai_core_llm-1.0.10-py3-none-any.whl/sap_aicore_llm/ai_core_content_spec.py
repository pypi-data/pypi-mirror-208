import pathlib
import yaml
from ai_core_sdk.content import ContentPackage

HERE = pathlib.Path(__file__).parent

workflow_yaml = HERE / 'pipelines' / 'workflows.yaml'
with workflow_yaml.open() as stream:
    workflows = yaml.safe_load(stream)


spec = ContentPackage(
    name='sap-ai-core-llm',
    workflows_base_path=workflow_yaml.parent,
    workflows=workflows,
    description='content package for large language models for SAP AI Core',
    version='1.0.0'
)