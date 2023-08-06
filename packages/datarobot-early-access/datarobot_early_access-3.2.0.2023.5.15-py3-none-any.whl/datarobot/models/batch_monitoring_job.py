#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

import io
from typing import Any, cast, Dict, List, Optional, TYPE_CHECKING, Union

import pandas as pd
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.job import AbstractSpecificJob
from datarobot.utils import pagination, to_api

from ..enums import JOB_TYPE, QUEUE_STATUS
from ..utils import logger
from .api_object import APIObject

LOG = logger.get_logger(__name__)

if TYPE_CHECKING:
    from mypy_extensions import TypedDict

    class IntakeSettings(TypedDict, total=False):
        """Intake settings typed dict"""

        type: str
        file: Optional[Union[str, pd.DataFrame, io.IOBase]]
        url: Optional[str]
        credential_id: Optional[str]
        data_store_id: Optional[str]
        query: Optional[str]
        table: Optional[str]
        schema: Optional[str]
        catalog: Optional[str]
        fetch_size: Optional[int]
        format: Optional[str]
        endpoint_url: Optional[str]

    class OutputSettings(TypedDict, total=False):
        """Output settings typed dict"""

        type: str
        path: Optional[str]
        url: Optional[str]
        credential_id: Optional[str]
        data_store_id: Optional[str]
        table: Optional[str]
        schema: Optional[str]
        catalog: Optional[str]
        statement_type: Optional[str]
        update_columns: Optional[List[str]]
        where_columns: Optional[List[str]]
        create_table_if_not_exists: Optional[bool]

    class CsvSettings(TypedDict):
        delimiter: Optional[str]
        quotechar: Optional[str]
        encoding: Optional[str]

    class Schedule(TypedDict):
        day_of_week: List[Union[int, str]]
        month: List[Union[int, str]]
        hour: List[Union[int, str]]
        minute: List[Union[int, str]]
        day_of_month: List[Union[int, str]]

    class CreatedBy(TypedDict):
        user_id: Optional[str]
        username: Optional[str]
        full_name: Optional[str]

    class MonitoringAggregation(TypedDict):
        retention_policy: str
        retention_value: int

    class PredictionColumMap(TypedDict):
        class_name: str
        column_name: str

    class MonitoringColumns(TypedDict):
        predictions_columns: Optional[Union[str, PredictionColumMap]]
        association_id_column: Optional[str]
        actuals_value_column: Optional[str]
        acted_upon_column: Optional[str]
        actuals_timestamp_column: Optional[str]

    class MonitoringOutputSettings(TypedDict):
        unique_row_identifier_columns: List[str]
        monitored_status_column: str

    class BatchMonitoringJobDict(TypedDict, total=False):
        """Batch monitoring job typed dict"""

        deployment_id: str
        intake_settings: IntakeSettings
        output_settings: Optional[OutputSettings]
        csv_settings: Optional[CsvSettings]
        num_concurrent: Optional[int]
        chunk_size: Optional[Union[int, str]]
        abort_on_error: bool
        download_timeout: Optional[int]
        download_read_timeout: Optional[int]
        upload_read_timeout: Optional[int]
        monitoring_aggregation: Optional[MonitoringAggregation]
        monitoring_columns: Optional[MonitoringColumns]
        monitoring_output_settings: Optional[MonitoringOutputSettings]


class BatchMonitoringJob(AbstractSpecificJob):
    """
    A Batch Monitoring Job is used to monitor data sets outside DataRobot app.

    Attributes
    ----------
    id : str
        the id of the job
    """

    _job_spec = t.Dict(
        {
            t.Key("num_concurrent"): Int(),
            t.Key("deployment_id"): String(),
            t.Key("intake_settings", optional=True): t.Dict().allow_extra("*"),
            t.Key("output_settings", optional=True): t.Dict().allow_extra("*"),
            t.Key("monitoring_aggregation", optional=True): t.Dict().allow_extra("*"),
            t.Key("monitoring_columns", optional=True): t.Dict().allow_extra("*"),
            t.Key("monitoring_output_settings", optional=True): t.Dict().allow_extra("*"),
        }
    ).allow_extra("*")
    _links = t.Dict(
        {t.Key("download", optional=True): String(allow_blank=True), t.Key("self"): String()}
    ).allow_extra("*")
    _converter_extra = t.Dict(
        {
            t.Key("percentage_completed"): t.Float(),
            t.Key("elapsed_time_sec"): Int(),
            t.Key("links"): _links,
            t.Key("job_spec"): _job_spec,
            t.Key("status_details"): String(),
        }
    ).allow_extra("*")
    _converter_common = t.Dict(
        {
            t.Key("id", optional=True): String,
            t.Key("status", optional=True): t.Enum(
                QUEUE_STATUS.ABORTED,
                QUEUE_STATUS.COMPLETED,
                QUEUE_STATUS.RUNNING,
                QUEUE_STATUS.INITIALIZING,
                "FAILED",
            ),
            t.Key("project_id", optional=True): String,
            t.Key("is_blocked", optional=True): t.Bool,
        }
    )
    _monitoring_columns = t.Dict(
        {
            t.Key("predictions_columns", optional=True): t.List(
                t.Dict({t.Key("class_name"): t.String(), t.Key("column_name"): t.String()})
            )
            | t.String(),
            t.Key("association_id_column", optional=True): t.String(),
            t.Key("actuals_value_column", optional=True): t.String(),
            t.Key("acted_upon_column", optional=True): t.String(),
            t.Key("actuals_timestamp_column", optional=True): t.String(),
        }
    )
    _monitoring_output_settings = t.Dict(
        {
            t.Key("unique_row_identifier_columns", optional=True): t.List(t.String),
            t.Key("monitored_status_column", optional=True): t.String(),
        }
    )
    _monitoring_aggregation = t.Dict(
        {
            t.Key("retention_policy", optional=True): t.Enum("samples", "percentage"),
            t.Key("retention_value", optional=True, default=0): t.Int(),
        }
    )

    @classmethod
    def _job_type(cls) -> str:
        return cast(str, JOB_TYPE.BATCH_MONITORING)

    @classmethod
    def _jobs_path(cls) -> str:
        return "batchJobs/"

    @classmethod
    def _job_path(cls, project_id: str, job_id: str) -> str:
        return f"batchJobs/{job_id}/"

    @classmethod
    def get(cls, project_id: Optional[str], job_id: str) -> BatchMonitoringJob:
        """Get batch monitoring job

        Attributes
        ----------
        job_id: str
            ID of batch job

        Returns
        -------
        BatchMonitoringJob
            Instance of BatchMonitoringJob
        """
        batch_job = super().get(project_id="", job_id=job_id)
        batch_job.id = job_id

        return batch_job


class BatchMonitoringJobDefinition(APIObject):  # pylint: disable=missing-class-docstring
    _path = "batchMonitoringJobDefinitions/"

    _user = t.Dict(
        {
            t.Key("username"): String(),
            t.Key("full_name", optional=True): String(),
            t.Key("user_id"): String(),
        }
    ).allow_extra("*")

    _schedule = t.Dict(
        {
            t.Key("day_of_week"): t.List(t.Or(String, Int)),
            t.Key("month"): t.List(t.Or(String, Int)),
            t.Key("hour"): t.List(t.Or(String, Int)),
            t.Key("minute"): t.List(t.Or(String, Int)),
            t.Key("day_of_month"): t.List(t.Or(String, Int)),
        }
    ).allow_extra("*")

    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("name"): String,
            t.Key("enabled"): t.Bool(),
            t.Key("schedule", optional=True): _schedule,
            t.Key("batch_monitoring_job"): BatchMonitoringJob._job_spec,
            t.Key("created"): String(),
            t.Key("updated"): String(),
            t.Key("created_by"): _user,
            t.Key("updated_by"): _user,
            t.Key("last_failed_run_time", optional=True): String(),
            t.Key("last_successful_run_time", optional=True): String(),
            t.Key("last_successful_run_time", optional=True): String(),
            t.Key("last_scheduled_run_time", optional=True): String(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        enabled: Optional[bool] = None,
        schedule: Optional[Schedule] = None,
        batch_monitoring_job: Optional[BatchMonitoringJobDict] = None,
        created: Optional[str] = None,
        updated: Optional[str] = None,
        created_by: Optional[CreatedBy] = None,
        updated_by: Optional[CreatedBy] = None,
        last_failed_run_time: Optional[str] = None,
        last_successful_run_time: Optional[str] = None,
        last_started_job_status: Optional[str] = None,
        last_scheduled_run_time: Optional[str] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.enabled = enabled
        self.schedule = schedule
        self.batch_monitoring_job = batch_monitoring_job

        self.created = created
        self.updated = updated
        self.created_by = created_by
        self.updated_by = updated_by

        self.last_failed_run_time = last_failed_run_time
        self.last_successful_run_time = last_successful_run_time
        self.last_started_job_status = last_started_job_status
        self.last_scheduled_run_time = last_scheduled_run_time

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def get(cls, batch_monitoring_job_definition_id: str) -> BatchMonitoringJobDefinition:
        """Get batch monitoring job definition

        Attributes
        ----------
        batch_monitoring_job_definition_id: str
            ID of batch monitoring job definition

        Returns
        -------
        BatchMonitoringJobDefinition
            Instance of BatchMonitoringJobDefinition

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> definition = dr.BatchMonitoringJobDefinition.get('5a8ac9ab07a57a0001be501f')
            >>> definition
            BatchMonitoringJobDefinition(60912e09fd1f04e832a575c1)
        """

        return cls.from_location(f"{cls._path}{batch_monitoring_job_definition_id}/")

    @classmethod
    def list(cls) -> List[BatchMonitoringJobDefinition]:
        """
        Get job all monitoring job definitions

        Returns
        -------
        List[BatchMonitoringJobDefinition]
            List of job definitions the user has access to see

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> definition = dr.BatchMonitoringJobDefinition.list()
            >>> definition
            [
                BatchMonitoringJobDefinition(60912e09fd1f04e832a575c1),
                BatchMonitoringJobDefinition(6086ba053f3ef731e81af3ca)
            ]
        """

        return list(
            cls.from_server_data(item) for item in pagination.unpaginate(cls._path, {}, cls._client)
        )

    @classmethod
    def create(
        cls,
        enabled: bool,
        batch_monitoring_job: BatchMonitoringJobDict,
        name: Optional[str] = None,
        schedule: Optional[Schedule] = None,
    ) -> BatchMonitoringJobDefinition:
        """
        Creates a new batch monitoring job definition to be run either at scheduled interval or as
        a manual run.

        Attributes
        ----------
        enabled : bool (default False)
            Whether the definition should be active on a scheduled basis. If True,
            `schedule` is required.

        batch_monitoring_job: dict
            The job specifications for your batch monitoring job.
            It requires the same job input parameters as used with BatchMonitoringJob

        name : string (optional)
            The name you want your job to be identified with. Must be unique across the
            organization's existing jobs.
            If you don't supply a name, a random one will be generated for you.

        schedule : dict (optional)
            The ``schedule`` payload defines at what intervals the job should run, which can be
            combined in various ways to construct complex scheduling terms if needed. In all
            the elements in the objects, you can supply either an asterisk ``["*"]`` denoting
            "every" time denomination or an array of integers (e.g. ``[1, 2, 3]``) to define
            a specific interval.

            The ``schedule`` payload is split up in the following items:

            **Minute:**

            The minute(s) of the day that the job will run. Allowed values are either ``["*"]``
            meaning every minute of the day or ``[0 ... 59]``

            **Hour:**
            The hour(s) of the day that the job will run. Allowed values are either ``["*"]``
            meaning every hour of the day or ``[0 ... 23]``.

            **Day of Month:**
            The date(s) of the month that the job will run. Allowed values are either
            ``[1 ... 31]`` or ``["*"]`` for all days of the month. This field is additive with
            ``dayOfWeek``, meaning the job will run both on the date(s) defined in this field
            and the day specified by ``dayOfWeek`` (for example, dates 1st, 2nd, 3rd, plus every
            Tuesday). If ``dayOfMonth`` is set to ``["*"]`` and ``dayOfWeek`` is defined,
            the scheduler will trigger on every day of the month that matches ``dayOfWeek``
            (for example, Tuesday the 2nd, 9th, 16th, 23rd, 30th).
            Invalid dates such as February 31st are ignored.

            **Month:**
            The month(s) of the year that the job will run. Allowed values are either
            ``[1 ... 12]`` or ``["*"]`` for all months of the year. Strings, either
            3-letter abbreviations or the full name of the month, can be used
            interchangeably (e.g., "jan" or "october").
            Months that are not compatible with ``dayOfMonth`` are ignored, for example
            ``{"dayOfMonth": [31], "month":["feb"]}``

            **Day of Week:**
            The day(s) of the week that the job will run. Allowed values are ``[0 .. 6]``,
            where (Sunday=0), or ``["*"]``, for all days of the week. Strings, either 3-letter
            abbreviations or the full name of the day, can be used interchangeably
            (e.g., "sunday", "Sunday", "sun", or "Sun", all map to ``[0]``.
            This field is additive with ``dayOfMonth``, meaning the job will run both on the
            date specified by ``dayOfMonth`` and the day defined in this field.

        Returns
        -------
        BatchMonitoringJobDefinition
            Instance of BatchMonitoringJobDefinition

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> job_spec = {
            ...    "num_concurrent": 4,
            ...    "deployment_id": "foobar",
            ...    "intake_settings": {
            ...        "url": "s3://foobar/123",
            ...        "type": "s3",
            ...        "format": "csv"
            ...    },
            ...    "output_settings": {
            ...        "url": "s3://foobar/123",
            ...        "type": "s3",
            ...        "format": "csv"
            ...    },
            ...}
            >>> schedule = {
            ...    "day_of_week": [
            ...        1
            ...    ],
            ...    "month": [
            ...        "*"
            ...    ],
            ...    "hour": [
            ...        16
            ...    ],
            ...    "minute": [
            ...        0
            ...    ],
            ...    "day_of_month": [
            ...        1
            ...    ]
            ...}
            >>> definition = BatchMonitoringJobDefinition.create(
            ...    enabled=False,
            ...    batch_monitoring_job=job_spec,
            ...    name="some_definition_name",
            ...    schedule=schedule
            ... )
            >>> definition
            BatchMonitoringJobDefinition(60912e09fd1f04e832a575c1)
        """

        BatchMonitoringJob._job_spec.check(batch_monitoring_job)

        job_spec = cast(Dict[str, Any], to_api(batch_monitoring_job))

        payload: Dict[str, Any] = {
            "name": name,
            "enabled": enabled,
        }

        if schedule:
            payload["schedule"] = to_api(schedule)

        payload.update(**job_spec)

        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(
        self,
        enabled: bool,
        batch_monitoring_job: Optional[BatchMonitoringJobDict] = None,
        name: Optional[str] = None,
        schedule: Optional[Schedule] = None,
    ) -> BatchMonitoringJobDefinition:
        """
        Updates a job definition with the changed specs.

        Takes the same input as :func:`~BatchMonitoringJobDefinition.create`

        Attributes
        ----------
        enabled : bool (default False)
            Same as ``enabled`` in :func:`~BatchMonitoringJobDefinition.create`.

        batch_monitoring_job: dict
            Same as ``batch_monitoring_job`` in :func:`~BatchMonitoringJobDefinition.create`.

        name : string (optional)
            Same as ``name`` in :func:`~BatchMonitoringJobDefinition.create`.

        schedule : dict
            Same as ``schedule`` in :func:`~BatchMonitoringJobDefinition.create`.

        Returns
        -------
        BatchMonitoringJobDefinition
            Instance of the updated BatchMonitoringJobDefinition

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> job_spec = {
            ...    "num_concurrent": 5,
            ...    "deployment_id": "foobar_new",
            ...    "intake_settings": {
            ...        "url": "s3://foobar/123",
            ...        "type": "s3",
            ...        "format": "csv"
            ...    },
            ...    "output_settings": {
            ...        "url": "s3://foobar/123",
            ...        "type": "s3",
            ...        "format": "csv"
            ...    },
            ...}
            >>> schedule = {
            ...    "day_of_week": [
            ...        1
            ...    ],
            ...    "month": [
            ...        "*"
            ...    ],
            ...    "hour": [
            ...        "*"
            ...    ],
            ...    "minute": [
            ...        30, 59
            ...    ],
            ...    "day_of_month": [
            ...        1, 2, 6
            ...    ]
            ...}
            >>> definition = BatchMonitoringJobDefinition.create(
            ...    enabled=False,
            ...    batch_monitoring_job=job_spec,
            ...    name="updated_definition_name",
            ...    schedule=schedule
            ... )
            >>> definition
            BatchMonitoringJobDefinition(60912e09fd1f04e832a575c1)
        """
        payload: Dict[str, Any] = {
            "enabled": enabled,
        }

        if name:
            payload["name"] = name

        if schedule:
            payload["schedule"] = to_api(schedule)

        if batch_monitoring_job:
            BatchMonitoringJob._job_spec.check(batch_monitoring_job)
            job_spec = cast(Dict[str, Any], to_api(batch_monitoring_job))
            payload.update(**job_spec)

        return self.from_server_data(
            self._client.patch(f"{self._path}{self.id}", data=payload).json()
        )

    def run_on_schedule(self, schedule: Schedule) -> BatchMonitoringJobDefinition:
        """
        Sets the run schedule of an already created job definition.

        If the job was previously not enabled, this will also set the job to enabled.

        Attributes
        ----------
        schedule : dict
            Same as ``schedule`` in :func:`~BatchMonitoringJobDefinition.create`.

        Returns
        -------
        BatchMonitoringJobDefinition
            Instance of the updated BatchMonitoringJobDefinition with the new / updated schedule.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> definition = dr.BatchMonitoringJobDefinition.create('...')
            >>> schedule = {
            ...    "day_of_week": [
            ...        1
            ...    ],
            ...    "month": [
            ...        "*"
            ...    ],
            ...    "hour": [
            ...        "*"
            ...    ],
            ...    "minute": [
            ...        30, 59
            ...    ],
            ...    "day_of_month": [
            ...        1, 2, 6
            ...    ]
            ...}
            >>> definition.run_on_schedule(schedule)
            BatchMonitoringJobDefinition(60912e09fd1f04e832a575c1)
        """

        payload = {
            "enabled": True,
            "schedule": to_api(schedule),
        }

        return self.from_server_data(
            self._client.patch(f"{self._path}{self.id}", data=payload).json()
        )

    def run_once(self) -> BatchMonitoringJob:
        """
        Manually submits a batch monitoring job to the queue, based off of an already
        created job definition.

        Returns
        -------
        BatchMonitoringJob
          Instance of BatchMonitoringJob

        Examples
        --------
        .. code-block:: python

          >>> import datarobot as dr
          >>> definition = dr.BatchMonitoringJobDefinition.create('...')
          >>> job = definition.run_once()
          >>> job.wait_for_completion()
        """

        definition = self.from_location(f"{self._path}{self.id}/")

        payload = {"jobDefinitionId": definition.id}

        response = self._client.post(
            f"{BatchMonitoringJob._jobs_path()}fromJobDefinition/", data=payload
        ).json()

        job_id = response["id"]
        return BatchMonitoringJob.get(None, job_id)

    def delete(self) -> None:
        """
        Deletes the job definition and disables any future schedules of this job if any.
        If a scheduled job is currently running, this will not be cancelled.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> definition = dr.BatchMonitoringJobDefinition.get('5a8ac9ab07a57a0001be501f')
            >>> definition.delete()
        """

        self._client.delete(f"{self._path}{self.id}/")
