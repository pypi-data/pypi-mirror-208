import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.tasks import WorkflowTaskBase


class Task(WorkflowTaskBase):
    def run(self) -> None:
        pass


@pytest.fixture
def base_task(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        yield task
    task.scratch.purge()
    task.constants._purge()


def test_apm_spans(base_task):
    """
    Given: A WorkflowTaskBase task
    When: Calling the task-specific apm_steps with weird inputs
    Then: Errors happen when they're supposed to and not when they're not supposed to
    """
    with pytest.raises(RuntimeError):
        with base_task.apm_processing_step("foo", span_type="bar"):
            pass

    with base_task.apm_task_step("foo", labels={"foo": "bar"}):
        pass


def test_tags(base_task):
    """
    Given: A WorkflowTaskBase task
    When: Creating, querying, and removing tags
    Then: The correct action is performed
    """
    path = base_task.scratch.workflow_base_path / "foo"
    path.touch()

    # Test assignment
    base_task.tag(path, ["tag1", "tag2"])
    assert list(base_task.read(["tag1", "tag2"])) == [path]

    # Test query
    assert sorted(base_task.tags(path)) == sorted(["tag1", "tag2"])

    # Test removal
    base_task.remove_tags(path, "tag1")
    assert base_task.tags(path) == ["tag2"]
