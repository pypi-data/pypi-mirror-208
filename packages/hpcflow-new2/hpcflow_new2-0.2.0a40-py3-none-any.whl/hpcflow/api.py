from hpcflow import __version__
from hpcflow.sdk import ConfigOptions
from hpcflow.sdk.app import BaseApp

config_options = ConfigOptions(
    directory_env_var="HPCFLOW_CONFIG_DIR",
    default_directory="~/.hpcflow-new",
    sentry_DSN="https://2463b288fd1a40f4bada9f5ff53f6811@o1180430.ingest.sentry.io/6293231",
    sentry_traces_sample_rate=1.0,
    sentry_env="main" if "a" in __version__ else "develop",
)

# built in template components (in this case, for demonstration purposes):
template_components = BaseApp.load_builtin_template_component_data(
    "hpcflow.sdk.data.template_components"
)

hpcflow = BaseApp(
    name="hpcflow",
    version=__version__,
    description="Computational workflow management",
    config_options=config_options,
    template_components=template_components,
    scripts_dir="sdk.demo.scripts",  # relative to root package
    pytest_args=[
        "--verbose",
        "--exitfirst",
    ],
)

load_config = hpcflow.load_config
reload_config = hpcflow.reload_config
make_workflow = hpcflow.make_workflow

# expose core classes that require access to the App instance:
Action = hpcflow.Action
ActionEnvironment = hpcflow.ActionEnvironment
ActionScope = hpcflow.ActionScope
ActionScopeType = hpcflow.ActionScopeType
ActionRule = hpcflow.ActionRule
Command = hpcflow.Command
Environment = hpcflow.Environment
Executable = hpcflow.Executable
ExecutableInstance = hpcflow.ExecutableInstance
ExecutablesList = hpcflow.ExecutablesList
ElementPropagation = hpcflow.ElementPropagation
ElementSet = hpcflow.ElementSet
FileSpec = hpcflow.FileSpec
InputFile = hpcflow.InputFile
InputFileGenerator = hpcflow.InputFileGenerator
InputSource = hpcflow.InputSource
InputSourceType = hpcflow.InputSourceType
InputValue = hpcflow.InputValue
Loop = hpcflow.Loop
OutputFileParser = hpcflow.OutputFileParser
Parameter = hpcflow.Parameter
ParameterValue = hpcflow.ParameterValue
ResourceList = hpcflow.ResourceList
ResourceSpec = hpcflow.ResourceSpec
SchemaInput = hpcflow.SchemaInput
SchemaOutput = hpcflow.SchemaOutput
Task = hpcflow.Task
TaskObjective = hpcflow.TaskObjective
TaskSchema = hpcflow.TaskSchema
TaskSourceType = hpcflow.TaskSourceType
ValueSequence = hpcflow.ValueSequence
Workflow = hpcflow.Workflow
WorkflowTask = hpcflow.WorkflowTask
WorkflowTemplate = hpcflow.WorkflowTemplate
