import logging
import os
import warnings
from pathlib import Path
from time import sleep
from typing import List, Union

from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from orjson import orjson

from picsellia import exceptions, utils
from picsellia.decorators import exception_handler
from picsellia.exceptions import (
    IllegalJobTransitionError,
    NotSupportedJobVersionError,
    WaitingAttemptsTimeout,
    WrongJobVersionError,
)
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.types.enums import JobRunStatus, JobStatus, ObjectDataType
from picsellia.types.schemas import JobRunSchema, JobSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Job(Dao):
    def __init__(self, connexion: Connexion, data: dict, version: int) -> None:
        self._version = version
        Dao.__init__(self, connexion, data)

    @property
    def status(self) -> Union[JobStatus, JobRunStatus]:
        """Status of this (Job)"""
        return self._status

    def __str__(self):
        return f"JobV{self._version} {self.id}: {self.status}"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        if self._version == 1:
            r = self.connexion.get(f"/sdk/job/{self.id}").json()
        elif self._version == 2:
            r = self.connexion.get(f"/sdk/v2/job/{self.id}").json()
        else:  # pragma: no cover
            raise NotSupportedJobVersionError(
                f"Unsupported Job version {self._version}"
            )
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> Union[JobSchema, JobRunSchema]:
        if self._version == 1:
            schema = JobSchema(**data)
        elif self._version == 2:
            schema = JobRunSchema(**data)
        else:  # pragma: no cover
            raise NotSupportedJobVersionError(
                f"Unsupported Job version {self._version}"
            )
        self._status = schema.status
        return schema

    @exception_handler
    @beartype
    def wait_for_done(self, blocking_time_increment: float = 1.0, attempts: int = 20):
        if self._version == 1:
            statuses = [
                JobStatus.SUCCESS,
                JobStatus.FAILED,
                JobStatus.TERMINATED,
            ]
        elif self._version == 2:
            statuses = [
                JobRunStatus.SUCCEEDED,
                JobRunStatus.FAILED,
                JobRunStatus.KILLED,
            ]
        else:  # pragma: no cover
            raise NotSupportedJobVersionError(
                f"Unsupported Job version {self._version}"
            )
        return self.wait_for_status(
            statuses,
            blocking_time_increment,
            attempts,
        )

    @exception_handler
    @beartype
    def wait_for_status(
        self,
        statuses: Union[
            str, JobStatus, JobRunStatus, List[Union[str, JobStatus, JobRunStatus]]
        ],
        blocking_time_increment: float = 1.0,
        attempts: int = 20,
    ) -> Union[JobStatus, JobRunStatus]:
        if (
            isinstance(statuses, JobRunStatus)
            or isinstance(statuses, JobStatus)
            or isinstance(statuses, str)
        ):
            statuses = [statuses]

        if self._version == 1:
            waited_statuses = [JobStatus.validate(status) for status in statuses]
        elif self._version == 2:
            waited_statuses = [JobRunStatus.validate(status) for status in statuses]
        else:  # pragma: no cover
            raise NotSupportedJobVersionError(
                f"Unsupported Job version {self._version}"
            )

        attempt = 0
        while attempt < attempts:
            self.sync()
            if self.status in waited_statuses:
                break

            sleep(blocking_time_increment)
            attempt += 1

        if attempt >= attempts:
            raise WaitingAttemptsTimeout(
                f"Job is still not in the status you've been waiting for, after {attempt} attempts."
                "Please wait a few more moment, or check"
            )

        return self.status

    @exception_handler
    @beartype
    def update_job_run_with_status(self, status: JobRunStatus):
        if self._version != 2:  # pragma: no cover
            raise WrongJobVersionError("You can't use this method with this job")

        if status == JobRunStatus.SUCCEEDED:
            r = self.connexion.post(f"/sdk/v2/job/{self.id}/succeed").json()
        elif status == JobRunStatus.FAILED:
            r = self.connexion.post(f"/sdk/v2/job/{self.id}/fail").json()
        elif status == JobRunStatus.RUNNING:
            r = self.connexion.post(f"/sdk/v2/job/{self.id}/running").json()
        else:
            raise IllegalJobTransitionError(
                f"You can change this job's status to {status}"
            )

        self.refresh(r)

    @exception_handler
    @beartype
    def send_logging(
        self,
        log: Union[str, list],
        part: str,
        final: bool = False,
        special: Union[str, bool, list] = False,
    ) -> None:
        """Send a logging experiment to the experiment .

        Arguments:
            log (str): Log content
            part (str): Logging Part
            final (bool, optional): True if Final line. Defaults to False.
            special (bool, optional): True if special log. Defaults to False.
        """
        if self._version != 2:  # pragma: no cover
            raise WrongJobVersionError("You can't use this method with this job")

        if not hasattr(self, "line_nb"):
            self.line_nb = 0

        to_send = {
            "line_nb": self.line_nb,
            "log": log,
            "final": final,
            "part": part,
            "special": special,
        }
        self.line_nb += 1
        self.connexion.post(
            f"/sdk/v2/job/{self.id}/logging",
            data=orjson.dumps(to_send),
        )

    @exception_handler
    @beartype
    def start_logging_chapter(self, name: str) -> None:
        """Print a log entry to the log .

        Arguments:
            name (str): Chapter name
        """
        utils.print_start_chapter_name(name)
        utils.print_line_return()

    @exception_handler
    @beartype
    def start_logging_buffer(self, length: int = 1) -> None:
        """Start logging buffer .

        Arguments:
            length (int, optional): Buffer length. Defaults to 1.
        """
        utils.print_logging_buffer(length)
        self.buffer_length = length

    @exception_handler
    @beartype
    def end_logging_buffer(self) -> None:
        """End the logging buffer ."""
        utils.print_logging_buffer(self.buffer_length)

    @exception_handler
    @beartype
    def store_logging_file(self, path: Union[str, Path]) -> str:
        """Store a logging file for this experiment.

        Examples:
            ```python
            experiment.store_logging_file("logs.txt")
            ```
        Arguments:
            path (str or Path): path to the file or folder.

        Raises:
            FileNotFoundException: No file found at the given path

        Returns:
            Object name of logging file as string
        """
        if self._version != 2:  # pragma: no cover
            raise WrongJobVersionError("You can't use this method with this job")

        if not os.path.exists(path):
            raise exceptions.FileNotFoundException(f"{path} not found")

        filename = os.path.split(path)[-1]
        object_name = self.connexion.generate_job_object_name(
            filename, ObjectDataType.LOGGING, self.id
        )
        _, is_large, _ = self.connexion.upload_file(object_name, path)

        payload = {"logging_object_name": object_name}

        r = self.connexion.post(
            f"/sdk/v2/job/{self.id}/logging/save",
            data=orjson.dumps(payload),
        ).json()
        return r["logging_object_name"]
