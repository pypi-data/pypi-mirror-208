"""Fedinesia - deletes old statuses for a fediverse account (Mastodon or Pleroma and forks)
Copyright (C) 2021, 2022, 2023  Mark S Burgunder.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import csv
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast

import aiocsv
import aiofiles
import arrow
from outdated import check_outdated
from rich import print

from . import Status
from . import __display_name__
from . import __package_name__
from . import __version__
from .config import Configuration

logger = logging.getLogger(__display_name__)


def check_updates() -> None:
    """Check if there is a newer version of Fedinesia available on PyPI."""
    is_outdated = False
    try:
        is_outdated, pypi_version = check_outdated(
            package=__package_name__,
            version=__version__,
        )
        if is_outdated:
            print(
                f"[bold][red]!!! New version of {__display_name__} ({pypi_version}) "
                f"is available on PyPI.org !!!\n"
            )
            logger.debug(
                "check_updates - New version of %s (%s) is available on PyPI.org",
                __display_name__,
                pypi_version,
            )
    except ValueError:
        print(
            "[yellow]Notice - Your version is higher than last published version on PyPI"
        )
        logger.debug(
            "check_updates - Notice - Your version is higher than last published version on PyPI"
        )
    except KeyError:
        logger.debug("check_updates() -> Project not found.")


AL = TypeVar("AL", bound="AuditLog")


@dataclass
class AuditLog:
    """Class to control the creation of an audit log and adding entries to
    it.
    """

    class Style(Enum):
        """Enumating different audit log file styles implemented."""

        PLAIN = 1
        CSV = 2

    audit_log: Any
    style: Style

    @classmethod
    async def open(
        cls: Type[AL],
        audit_log_file: str,
        style: Optional[str],
    ) -> AL:
        """Open audit log file for writing and appending new log entries.

        :returns: a new AuditLog instance.
        """
        audit_log = await aiofiles.open(file=audit_log_file, mode="at")
        if style:
            log_style = AuditLog.Style[style]
        else:
            log_style = AuditLog.Style.PLAIN

        if (
            log_style == AuditLog.Style.CSV
            and os.fstat(audit_log.fileno()).st_size == 0
        ):
            await AuditLog._add_csv_header(audit_log)

        return cls(audit_log=audit_log, style=log_style)

    async def close(self: AL) -> None:
        """Close audit log file."""
        self.audit_log.close()

    async def add_entry(self: AL, status: Status) -> None:
        """Append an entry/status details to the audit log file."""
        if self.style == AuditLog.Style.PLAIN:
            await self._add_plain_entry(status)
        elif self.style == AuditLog.Style.CSV:
            await self._add_csv_entry(status)
        else:
            print(f"Unsupported log style passed: {self.style=}")

    async def _add_plain_entry(self: AL, status: Status) -> None:
        """Append a plain text entry/status details to the audit log file."""
        entry = (
            f"{arrow.now().format('YYYY-MM-DD hh:mm:ss')} -"
            f" Removed {'poll' if status.get('poll', False) else 'status'} {status.get('url')}"
            f" created @ {status.get('created_at')}"
            f" with {status.get('visibility')} visibility, {len(status.get('media_attachments', []))} attachments."
            f" This status was reblogged {status.get('reblogs_count')} times and"
            f" favourited {status.get('favourites_count')} times."
            f" The status was {'pinned' if status.get('pinned') else 'not pinned'}.\n"
        )
        await self.audit_log.write(entry)

    async def _add_csv_entry(self: AL, status: Status) -> None:
        """Append a csv formatted status details to the audit log file."""
        csv_writer = aiocsv.writers.AsyncWriter(
            asyncfile=self.audit_log,
            quoting=csv.QUOTE_ALL,
        )
        record = [
            arrow.now(),
            "poll" if status.get("poll", False) else "status",
            status.get("url"),
            arrow.get(status.get("created_at", 0)).to(tz="local"),
            status.get("visibility"),
            len(status.get("media_attachments", [])),
            status.get("reblogs_count"),
            status.get("favourites_count"),
            status.get("pinned"),
        ]
        await csv_writer.writerow(row=record)

    @staticmethod
    async def _add_csv_header(csv_file: Any) -> None:
        """Write CSV header line to the audit log file.

        This method is normally called when an audit log file is being
        initially created before writing any other entries to the audit
        log; i.e. The record it writes will be the header record for the
        CSV file.
        """
        csv_writer = aiocsv.writers.AsyncWriter(
            asyncfile=csv_file, quoting=csv.QUOTE_ALL
        )
        record = [
            "date and time of deletion",
            "type of status,",
            "url of status before deletion",
            "date and time deleted status was created",
            "visibility",
            "# of media_attachments",
            "reblogs_count",
            "favourites_count",
            "pinned",
        ]
        await csv_writer.writerow(row=record)


def should_keep(  # noqa PLR0911
    status: Status, oldest_to_keep: arrow.Arrow, config: Configuration
) -> bool:
    """Determine if status should be kept."""
    status_created_at = arrow.get(cast(int, status.get("created_at")))
    if status_created_at >= oldest_to_keep:
        return True

    if config.bot.skip_deleting_bookmarked and bool(status.get("bookmarked")):
        return True

    if config.bot.skip_deleting_faved and bool(status.get("favourited")):
        return True

    if config.bot.skip_deleting_pinned and bool(status.get("pinned")):
        return True

    if config.bot.skip_deleting_poll and bool(status.get("poll")):
        return True

    if config.bot.skip_deleting_dm and status.get("visibility") == "direct":
        return True

    medias = status.get("media_attachments")
    if (
        config.bot.skip_deleting_media
        and isinstance(medias, list)
        and bool(len(medias))
    ):
        return True

    favourites = status.get("favourites_count", 0)
    if (
        config.bot.skip_deleting_faved_at_least
        and favourites >= config.bot.skip_deleting_faved_at_least
    ):
        return True

    reblogs = status.get("reblogs_count", 0)
    if (
        config.bot.skip_deleting_boost_at_least
        and reblogs >= config.bot.skip_deleting_boost_at_least
    ):
        return True

    if config.bot.skip_deleting_reactions_at_least:
        reactions_threshold = config.bot.skip_deleting_reactions_at_least
    else:
        reactions_threshold = 0

    return enough_reactions_to_keep(
        status=status,
        reactions_threshold=reactions_threshold,
    )


def enough_reactions_to_keep(status: Status, reactions_threshold: int) -> bool:
    """Check if emoji_reactions are reported in status and check of they are at least at the
    threshold for keeping the status.
    Note: Reactions are a Pleroma specific feature.

    :param status: Status being examined for reactions
    :param reactions_threshold: Minimum number of reactions to consider the check to be met

    :returns:
        True if the total number of reactions to status is equal to or more than the reactions_threshold.
        False in any other case, including if the status does not contain any reaction counts at all.
    """
    if not (pleroma := status.get("pleroma")):
        return False

    if not (reactions := pleroma.get("emoji_reactions")):
        return False

    logger.debug(
        "enough_reactions_to_keep - reactions_threshold: %s - emoji_reactions:\n%s",
        reactions_threshold,
        json.dumps(reactions, indent=4),
    )

    total_reactions = 0
    for reaction in reactions:
        if emo_count := reaction.get("count"):
            total_reactions += emo_count

    return total_reactions >= reactions_threshold
