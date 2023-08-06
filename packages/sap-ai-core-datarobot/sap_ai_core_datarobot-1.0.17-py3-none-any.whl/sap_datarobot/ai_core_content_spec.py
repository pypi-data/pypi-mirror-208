import pathlib
import yaml
from ai_core_sdk.content import ContentPackage

HERE = pathlib.Path(__file__).parent

workflow_yaml = HERE / 'pipelines' / 'workflows.yaml'
with workflow_yaml.open() as stream:
    workflows = yaml.safe_load(stream)


spec = ContentPackage(
    name='sap_datarobot',
    workflows_base_path=workflow_yaml.parent,
    workflows=workflows,
    description='Content Package to integrate DataRobot with SAP AI Core',
    version='0.0.1'
)