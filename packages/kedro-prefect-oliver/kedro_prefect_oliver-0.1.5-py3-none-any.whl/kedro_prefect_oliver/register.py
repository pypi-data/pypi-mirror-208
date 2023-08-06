from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from kedro.framework.project import pipelines, find_pipelines
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.io import DataCatalog, MemoryDataSet
from kedro.runner import run_node
from kedro.pipeline.node import Node
from pluggy import PluginManager

from prefect.infrastructure.kubernetes import KubernetesJob
from prefect.task_runners import SequentialTaskRunner
from prefect import flow, get_run_logger, task
from prefect.deployments import Deployment
from prefect.filesystems import GCS
import prefect

import pendulum
import click

from prefect.utilities.hashing import file_hash
from prefect.server.schemas.schedules import (
    CronSchedule,
    IntervalSchedule,
    RRuleSchedule,
)


class KedroInitTask(object):
    """Task to initialize KedroSession"""

    def __init__(
        self,
        pipeline_name: str,
        project_path: Union[Path, str] = None,
        env: str = None,
        extra_params: Dict[str, Any] = None,
        name: str = None,
    ):
        self.project_path = Path(project_path or Path.cwd()).resolve()
        self.extra_params = extra_params
        self.pipeline_name = pipeline_name
        self.env = env
        self.name = name or "KedroInitTask"

    def run(self) -> Dict[str, Union[DataCatalog, str]]:
        """
        Initializes a Kedro session and returns the DataCatalog and
        KedroSession
        """
        # bootstrap project within task / flow scope
        logger = get_run_logger()
        logger.info("Bootstrapping project")
        bootstrap_project(self.project_path)

        logger.info("Creating session")
        session = KedroSession.create(
            project_path=self.project_path,
            env=self.env,
            extra_params=self.extra_params,  # noqa: E501
        )

        # Note that for logging inside a Prefect task self.logger is used.
        logger.info("Session created with ID %s", session.session_id)
        pipeline = pipelines.get(self.pipeline_name)
        context = session.load_context()
        catalog = context.catalog
        unregistered_ds = pipeline.data_sets() - set(catalog.list())  # NOQA
        for ds_name in unregistered_ds:
            catalog.add(ds_name, MemoryDataSet())
        return {
            "catalog": catalog,
            "sess_id": session.session_id,
            "hook_manager": session._hook_manager,
        }  # NOQA


class KedroTask(object):
    """Kedro node as a Prefect task."""

    def __init__(self, node: Node, name: str = None):
        self._node = node
        self.name = name or node.name

    def run(self, task_dict: Dict[str, Union[DataCatalog, str, PluginManager]]) -> None:
        run_node(
            self._node,
            task_dict["catalog"],
            task_dict["hook_manager"],
            False,
            task_dict["sess_id"],
        )


def instantiate_task(
    node: Node,
    tasks: Dict[str, Dict[str, Union[KedroTask, List[KedroTask]]]],
) -> Tuple[KedroTask, Dict[str, Dict[str, Union[KedroTask, List[KedroTask]]]]]:
    """
    Function pulls node task from <tasks> dictionary. If node task not
    available in <tasks> the function instantiates the tasks and adds
    it to <tasks>. In this way we avoid duplicate instantiations of
    the same node task.

    Args:
        node: Kedro node for which a Prefect task is being created.
        tasks: dictionary mapping node names to a dictionary containing
        node tasks and parent node tasks.

    Returns: Prefect task for the passed node and task dictionary.

    """
    if tasks.get(node._unique_key) is not None:
        node_task = tasks[node._unique_key]["task"]
    else:
        node_task = KedroTask(node)
        tasks[node._unique_key] = {"task": node_task}

    # return tasks as it is mutated. We want to make this obvious to the user.
    return node_task, tasks  # type: ignore[return-value]


@task
def run_kedro_task(
    kedro_task: Union[KedroInitTask, KedroTask],
    task_dict: Union[None, Dict[str, Union[DataCatalog, str]]] = None,
) -> Union[Dict[str, Union[DataCatalog, str]], None]:
    """Run a Kedro node as a Prefect task."""
    if task_dict is None:
        get_run_logger().info("Initializing Kedro session")
        task_dict = kedro_task.run()
        return task_dict
    else:
        print("Running Kedro node")
        get_run_logger().info("Running node %s", kedro_task._node.name)
        kedro_task.run(task_dict)
        return None


def init_kedro_nodes(
    pipeline_name: str, env: str
) -> Dict[
    str,
    Union[
        KedroInitTask,
        Dict[str, List[KedroTask]],
        Dict[str, Dict[str, Union[KedroTask, List[KedroTask]]]],
    ],
]:
    """Register a Kedro pipeline as a Prefect flow."""
    logger = get_run_logger()
    logger.info("Initializing Kedro nodes")
    project_path = Path.cwd()
    logger.info("Project path: %s", project_path)
    metadata = bootstrap_project(project_path)
    logger.info("Project name: %s", metadata.project_name)
    logger.debug("Pipelines: %s", find_pipelines())
    pipeline = pipelines.get(pipeline_name)

    tasks = {}
    for node, parent_nodes in pipeline.node_dependencies.items():
        # Use a function for task instantiation which avoids duplication of
        # tasks
        _, tasks = instantiate_task(node, tasks)

        parent_tasks = []
        for parent in parent_nodes:
            parent_task, tasks = instantiate_task(parent, tasks)
            parent_tasks.append(parent_task)

        tasks[node._unique_key]["parent_tasks"] = parent_tasks

    # Below task is used to instantiate a KedroSession within the scope of a
    # Prefect flow
    init_task = KedroInitTask(
        pipeline_name=pipeline_name,
        project_path=project_path,
        env=env,
        name="init_task",
    )

    return {"init_task": init_task, "tasks": tasks}


@flow(task_runner=SequentialTaskRunner(), validate_parameters=False, log_prints=False)
def create_pipeline(pipeline_name: str, env: str) -> None:
    """Create a Prefect flow from a Kedro pipeline."""

    kedro_tasks = init_kedro_nodes(pipeline_name, env)
    init_task = kedro_tasks["init_task"]
    tasks = kedro_tasks["tasks"]

    run_kedro_init_task = run_kedro_task.with_options(name=init_task.name)
    task_dict = run_kedro_init_task.submit(init_task)
    task_dependencies = {
        kedro_task["task"]: kedro_task["parent_tasks"] for kedro_task in tasks.values()
    }
    todo_nodes = set([kedro_task["task"] for kedro_task in tasks.values()])
    submitted_tasks: Dict[KedroTask, prefect.Task] = {}
    while True:
        ready = {
            node
            for node in todo_nodes
            if set(task_dependencies[node]) <= submitted_tasks.keys()
        }
        todo_nodes -= ready
        for node in ready:
            run_kedro_node_task = run_kedro_task.with_options(name=node.name)
            future = run_kedro_node_task.submit(
                node,
                task_dict,
                wait_for=[submitted_tasks[t] for t in task_dependencies[node]],
            )
            submitted_tasks[node] = future

        if not todo_nodes:
            break


def create_prefect_schedule(
    interval: float = None,
    anchor_date: str = None,
    rrule_string: str = None,
    cron_string: str = None,
    day_or: bool = True,
    timezone: str = "America/New_York",
) -> Union[IntervalSchedule, CronSchedule, RRuleSchedule, None]:
    """Create a Prefect schedule for a Kedro pipeline."""

    if sum(option is not None for option in [interval, rrule_string, cron_string]) > 1:
        raise ValueError(
            "Exactly one of interval, rrule_string, or cron_string must be provided."
        )

    if anchor_date and not interval:
        raise ValueError(
            "An anchor date can only be provided with an interval schedule."
        )

    schedule = None
    if interval is not None:
        if anchor_date:
            try:
                pendulum.parse(anchor_date)
            except ValueError:
                raise ValueError("The anchor date must be a valid date string.")
        interval_schedule = {
            "interval": interval,
            "anchor_date": anchor_date,
            "timezone": timezone,
        }
        schedule = IntervalSchedule(
            **{k: v for k, v in interval_schedule.items() if v is not None}
        )

    if cron_string is not None:
        cron_schedule = {
            "cron": cron_string,
            "day_or": day_or,
            "timezone": timezone,
        }
        schedule = CronSchedule(
            **{k: v for k, v in cron_schedule.items() if v is not None}
        )

    if rrule_string is not None:
        # a timezone in the `rrule_string` gets ignored by the RRuleSchedule constructor
        if "TZID" in rrule_string and not timezone:
            raise ValueError(
                "A timezone must be provided if the rrule string contains a timezone."
            )
        schedule = RRuleSchedule(rrule=rrule_string, timezone=timezone)

    return schedule


def deploy_flow(
    project: str,
    entrypoint: str,
    bucket: str,
    kedro_package: str,
    kedro_pipeline: str = None,
    tags: List[str] = None,
    env: str = None,
    dev: bool = False,
    interval: float = None,
    anchor_date: str = None,
    rrule_string: str = None,
    cron_string: str = None,
    day_or: bool = True,
    timezone: str = "America/New_York",
) -> None:
    """Deploy a Kedro pipeline as a Prefect flow."""

    kedro_pipeline = kedro_pipeline or "__default__"
    # get the dependencies and installs
    requires = None
    if dev:
        with open("src/requirements.lock", encoding="utf-8") as f:
            # Make sure we strip all comments and options (e.g "--extra-index-url")
            # that arise from a modified pip.conf file that configure global options
            # when running kedro build-reqs
            requires = []
            for line in f:
                req = line.split("#", 1)[0].strip()
                if req and not req.startswith("--"):
                    requires.append(req)
        requires = " ".join([f"{req}" for req in requires])

    version = file_hash(str(Path(__file__).resolve()))

    gcs_path = (
        kedro_package.replace("_", "-") + "/" + kedro_pipeline.replace("_", "-")
    ).replace(" ", "")
    gcs_block_name = gcs_path.replace("/", "-")
    gcs_block = GCS(bucket_path=bucket + "/" + gcs_path, project=project)
    gcs_block.save(gcs_block_name, overwrite=True)

    job_name = f"{kedro_package.replace('_', '-')}-kubernetes-job"
    kubernetes_job = KubernetesJob.load(job_name)

    parameters = {"pipeline_name": kedro_pipeline, "env": env}

    deployment = Deployment.build_from_flow(
        entrypoint=entrypoint,
        flow=create_pipeline.with_options(
            name=f"{kedro_package}.{kedro_pipeline}", version=version
        ),
        name="kubernetes-job",
        work_queue_name="kubernetes",
        tags=["kubernetes", "kedro"] + tags or [],
        storage=gcs_block,
        infrastructure=kubernetes_job,
        parameters=parameters,
        infra_overrides={
            "env": {"EXTRA_PIP_PACKAGES": requires},
        }
        if requires
        else {},
        schedule=create_prefect_schedule(
            interval, anchor_date, rrule_string, cron_string, day_or, timezone
        ),
    )
    dep_id = deployment.apply()
    print("Deployment ID: {}".format(dep_id))


@click.command()
@click.option("--project", type=str, required=True)
@click.option("--entrypoint", type=str, required=True)
@click.option("--bucket", type=str, required=True)
@click.option("--kedro_package", type=str, required=True)
@click.option("--kedro_pipeline", default=None)
@click.option("--tags", multiple=True, type=str, default=None)
@click.option(
    "--env",
    "-e",
    type=str,
    default=None,
    help="Kedro environment to use (e.g. local, dev, prod, etc.",
)
@click.option(
    "--dev",
    "-d",
    type=bool,
    default=False,
    help="When True, use project dependencies from requirements.lock",
)
@click.option(
    "--interval",
    type=float,
    default=None,
    help="An interval to schedule on, specified in seconds",
)
@click.option(
    "--anchor_date",
    type=str,
    default=None,
    help="The anchor date for an interval schedule",
)
@click.option(
    "--rrule", type=str, default=None, help="Deployment schedule rrule string"
)
@click.option("--cron", type=str, default=None, help="Deployment schedule cron string")
@click.option(
    "--day_or",
    type=bool,
    default=True,
    help="Control how croniter handles `day` and `day_of_week` entries",
)
@click.option(
    "--timezone",
    type=str,
    default="America/New_York",
    help="Deployment schedule timezone",
)
def deploy_prefect_flow(
    project: str,
    entrypoint: str,
    bucket: str,
    kedro_package: str,
    kedro_pipeline: str,
    tags: List[str],
    env: str,
    dev: bool,
    interval: float,
    anchor_date: str,
    rrule: str,
    cron: str,
    day_or: bool,
    timezone: str,
) -> None:
    deploy_flow(
        project,
        entrypoint,
        bucket,
        kedro_package,
        kedro_pipeline,
        tags,
        env,
        dev,
        interval,
        anchor_date,
        rrule,
        cron,
        day_or,
        timezone,
    )


if __name__ == "__main__":
    print("Deploying Prefect flow...")
    # Standalone mode is false to make the function callable from other scripts
    # Standalone mode is a click parameter
    deploy_prefect_flow(standalone_mode=False)
