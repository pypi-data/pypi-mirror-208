import numpy as np
import pytest
from hpcflow.api import (
    hpcflow,
    InputValue,
    Parameter,
    SchemaInput,
    Task,
    TaskSchema,
    ValueSequence,
    Workflow,
    WorkflowTemplate,
    InputSource,
    InputSourceType,
    TaskSourceType,
)
from hpcflow.sdk.core.errors import MissingInputs


def test_input_source_class_method_local():
    assert InputSource.local() == InputSource(InputSourceType.LOCAL)


def test_input_source_class_method_default():
    assert InputSource.default() == InputSource(InputSourceType.DEFAULT)


def test_input_source_class_method_task():
    task_ref = 0
    assert InputSource.task(task_ref) == InputSource(
        source_type=InputSourceType.TASK, task_ref=task_ref
    )


def test_input_source_class_method_import():
    import_ref = (
        0  # TODO: interface to imports (and so how to reference) is not yet decided
    )
    assert InputSource.import_(import_ref) == InputSource(
        InputSourceType.IMPORT, import_ref=import_ref
    )


def test_input_source_class_method_task_same_default_task_source_type():
    task_ref = 0
    assert (
        InputSource(InputSourceType.TASK, task_ref=task_ref).task_source_type
        == InputSource.task(task_ref=task_ref).task_source_type
    )


def test_input_source_validate_source_type_string_local():
    assert InputSource("local") == InputSource(InputSourceType.LOCAL)


def test_input_source_validate_source_type_string_default():
    assert InputSource("default") == InputSource(InputSourceType.DEFAULT)


def test_input_source_validate_source_type_string_task():
    task_ref = 0
    assert InputSource("task", task_ref=task_ref) == InputSource(
        InputSourceType.TASK, task_ref=task_ref
    )


def test_input_source_validate_source_type_string_import():
    import_ref = (
        0  # TODO: interface to imports (and so how to reference) is not yet decided
    )
    assert InputSource("import", import_ref=import_ref) == InputSource(
        InputSourceType.IMPORT, import_ref=import_ref
    )


def test_input_source_validate_source_type_raise_on_unknown_string():
    with pytest.raises(ValueError):
        InputSource("bad_source_type")


def test_input_source_validate_task_source_type_string_any():
    task_ref = 0
    assert InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type="any"
    ) == InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type=TaskSourceType.ANY
    )


def test_input_source_validate_task_source_type_string_input():
    task_ref = 0
    assert InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type="input"
    ) == InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type=TaskSourceType.INPUT
    )


def test_input_source_validate_task_source_type_string_output():
    task_ref = 0
    assert InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type="output"
    ) == InputSource(
        InputSourceType.TASK, task_ref=task_ref, task_source_type=TaskSourceType.OUTPUT
    )


def test_input_source_validate_task_source_type_raise_on_unknown_string():
    task_ref = 0
    with pytest.raises(ValueError):
        InputSource(
            InputSourceType.TASK,
            task_ref=task_ref,
            task_source_type="bad_task_source_type",
        )


def test_input_source_to_string_local():
    assert InputSource.local().to_string() == "local"


def test_input_source_to_string_default():
    assert InputSource.default().to_string() == "default"


def test_input_source_to_string_task_output():
    task_ref = 0
    assert (
        InputSource.task(task_ref, task_source_type="output").to_string()
        == f"task.{task_ref}.output"
    )


def test_input_source_to_string_task_input():
    task_ref = 0
    assert (
        InputSource.task(task_ref, task_source_type="input").to_string()
        == f"task.{task_ref}.input"
    )


def test_input_source_to_string_task_any():
    task_ref = 0
    assert (
        InputSource.task(task_ref, task_source_type="any").to_string()
        == f"task.{task_ref}.any"
    )


def test_input_source_to_string_import():
    import_ref = 0
    assert InputSource.import_(import_ref).to_string() == f"import.{import_ref}"


def test_input_source_from_string_local():
    assert InputSource.from_string("local") == InputSource(InputSourceType.LOCAL)


def test_input_source_from_string_default():
    assert InputSource.from_string("default") == InputSource(InputSourceType.DEFAULT)


def test_input_source_from_string_task():
    assert InputSource.from_string("task.0.output") == InputSource(
        InputSourceType.TASK, task_ref=0, task_source_type=TaskSourceType.OUTPUT
    )


def test_input_source_from_string_task_same_default_task_source():
    task_ref = 0
    assert InputSource.from_string(f"task.{task_ref}") == InputSource(
        InputSourceType.TASK, task_ref=task_ref
    )


def test_input_source_from_string_import():
    import_ref = 0
    assert InputSource.from_string(f"import.{import_ref}") == InputSource(
        InputSourceType.IMPORT, import_ref=import_ref
    )


@pytest.fixture
def param_p1():
    return Parameter("p1")


@pytest.fixture
def param_p2():
    return Parameter("p2")


@pytest.fixture
def param_p3():
    return Parameter("p3")


@pytest.fixture
def null_config(tmp_path):
    hpcflow.load_config(config_dir=tmp_path)


@pytest.mark.skip(reason="Need to add e.g. parameters of the workflow to the app data.")
def test_specified_sourceable_elements_subset(
    null_config, param_p1, param_p2, param_p3, tmp_path
):

    param_p1 = SchemaInput(param_p1, default_value=1001)
    param_p2 = SchemaInput(param_p2, default_value=np.array([2002, 2003]))
    param_p3 = SchemaInput(param_p3)

    s1 = TaskSchema("ts1", actions=[], inputs=[param_p1], outputs=[param_p3])
    s2 = TaskSchema("ts2", actions=[], inputs=[param_p2, param_p3])

    t1 = Task(
        schemas=s1,
        sequences=[
            ValueSequence("inputs.p1", values=[101, 102], nesting_order=0),
        ],
    )
    t2 = Task(
        schemas=s2,
        inputs=[InputValue(param_p2, 201)],
        sourceable_elements=[0],
        nesting_order={"inputs.p3": 1},
    )

    wkt = WorkflowTemplate(name="w1", tasks=[t1, t2])
    wk = Workflow.from_template(wkt, path=tmp_path)

    assert (
        wk.tasks[1].num_elements == 1
        and wk.tasks[1].elements[0].input_sources["inputs.p3"] == "element.0.OUTPUT"
    )


@pytest.mark.skip(reason="Need to add e.g. parameters of the workflow to the app data.")
def test_specified_sourceable_elements_all_available(
    null_config, param_p1, param_p2, param_p3, tmp_path
):

    param_p1 = SchemaInput(param_p1, default_value=1001)
    param_p2 = SchemaInput(param_p2, default_value=np.array([2002, 2003]))
    param_p3 = SchemaInput(param_p3)

    s1 = TaskSchema("ts1", actions=[], inputs=[param_p1], outputs=[param_p3])
    s2 = TaskSchema("ts2", actions=[], inputs=[param_p2, param_p3])

    t1 = Task(
        schemas=s1,
        sequences=[
            ValueSequence("inputs.p1", values=[101, 102], nesting_order=0),
        ],
    )
    t2 = Task(
        schemas=s2,
        inputs=[InputValue(param_p2, 201)],
        sourceable_elements=[0, 1],
        nesting_order={"inputs.p3": 1},
    )

    wkt = WorkflowTemplate(name="w1", tasks=[t1, t2])
    wk = Workflow.from_template(wkt, path=tmp_path)

    assert (
        wk.tasks[1].num_elements == 2
        and wk.tasks[1].elements[0].input_sources["inputs.p3"] == "element.0.OUTPUT"
        and wk.tasks[1].elements[1].input_sources["inputs.p3"] == "element.1.OUTPUT"
    )


@pytest.mark.skip(reason="Need to add e.g. parameters of the workflow to the app data.")
def test_no_sourceable_elements_so_raise_missing(
    null_config, param_p1, param_p2, param_p3, tmp_path
):

    param_p1 = SchemaInput(param_p1, default_value=1001)
    param_p2 = SchemaInput(param_p2, default_value=np.array([2002, 2003]))
    param_p3 = SchemaInput(param_p3)

    s1 = TaskSchema("ts1", actions=[], inputs=[param_p1], outputs=[param_p3])
    s2 = TaskSchema("ts2", actions=[], inputs=[param_p2, param_p3])

    t1 = Task(schemas=s1, inputs=[InputValue(param_p1, 101)])
    t2 = Task(
        schemas=s2,
        inputs=[InputValue(param_p2, 201)],
        sourceable_elements=[],
    )

    wkt = WorkflowTemplate(name="w1", tasks=[t1, t2])

    with pytest.raises(MissingInputs):
        _ = Workflow.from_template(wkt, path=tmp_path)


@pytest.mark.skip(reason="Need to add e.g. parameters of the workflow to the app data.")
def test_no_sourceable_elements_so_default_used(
    null_config, param_p1, param_p2, param_p3, tmp_path
):

    param_p1 = SchemaInput(param_p1, default_value=1001)
    param_p2 = SchemaInput(param_p2, default_value=np.array([2002, 2003]))
    param_p3 = SchemaInput(param_p3, default_value=3001)

    s1 = TaskSchema("ts1", actions=[], inputs=[param_p1], outputs=[param_p3])
    s2 = TaskSchema("ts2", actions=[], inputs=[param_p2, param_p3])

    t1 = Task(schemas=s1, inputs=[InputValue(param_p1, 101)])
    t2 = Task(
        schemas=s2,
        inputs=[InputValue(param_p2, 201)],
        sourceable_elements=[],
    )

    wkt = WorkflowTemplate(name="w1", tasks=[t1, t2])
    wk = Workflow.from_template(wkt, path=tmp_path)

    assert wk.tasks[1].elements[0].input_sources["inputs.p3"] == "default"
