import typing
import datetime as dt
import time

from .base_client import Seam as BaseClient
from .environment import SeamEnvironment
from .resources.access_codes.client import AccessCodesClient
from .resources.action_attempts.client import ActionAttemptsClient
from . import UpdateAccessCodeResponse, ActionAttemptId, ActionAttempt, AccessCode


# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class Seam(BaseClient):
    def __init__(self, *, environment: SeamEnvironment = SeamEnvironment.PRODUCTION, token: str):
        super().__init__(environment=environment, token=token)
        self.access_codes = AccessCodes(
            environment=self._environment,
            token=self._token,
            action_attempts_client=self.action_attempts,
        )


class AccessCodes(AccessCodesClient):
    def __init__(self, *, environment: SeamEnvironment, token: str, action_attempts_client: ActionAttemptsClient):
        super().__init__(environment=environment, token=token)
        self._action_attempts_client = action_attempts_client

    def update_and_wait_until_ready(  # type: ignore
        self,
        *,
        access_code_id: str,
        name: typing.Optional[str] = OMIT,
        code: typing.Optional[str] = OMIT,
        starts_at: typing.Optional[dt.datetime] = OMIT,
        ends_at: typing.Optional[dt.datetime] = OMIT,
    ) -> AccessCode:
        res = super().update(
            access_code_id=access_code_id,
            name=name,
            code=code,
            starts_at=starts_at,
            ends_at=ends_at
        )

        action_attempt = self._poll_until_ready(
            res.action_attempt.action_attempt_id
        )

        return action_attempt.result.access_code

    def _poll_until_ready(self, action_attempt: ActionAttemptId) -> ActionAttempt:
        updated_action_attempt: typing.Optional[ActionAttempt] = None
        while (
            updated_action_attempt is None
            or updated_action_attempt.status == "pending"
        ):
            updated_action_attempt = self._action_attempts_client.get(action_attempt_id=action_attempt)
            time.sleep(0.25)

        if updated_action_attempt.status == "error":
            error_type = None
            error_message = None
            if updated_action_attempt.error is not None:
                error_type = updated_action_attempt.error.type
                error_message = updated_action_attempt.error.message
            raise ActionAttemptFailedException(
                action_attempt_id=updated_action_attempt.action_attempt_id,
                action_type=updated_action_attempt.action_type,
                error_type=error_type,
                error_message=error_message,
            )

        return updated_action_attempt


class ActionAttemptFailedException(Exception):
    def __init__(
        self,
        action_attempt_id: typing.Optional[ActionAttemptId] = None,
        action_type: typing.Optional[str] = None,
        error_type: typing.Optional[str] = None,
        error_message: typing.Optional[str] = None,
    ):
        self.action_attempt_id = action_attempt_id
        self.action_type = action_type
        self.error_type = error_type
        self.error_message = error_message
        super().__init__(
            f'Action Attempt for "{action_type}" Failed. {error_type}: {error_message} (action_attempt_id={action_attempt_id})'
        )
