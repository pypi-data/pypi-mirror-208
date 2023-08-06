"""Fedinesia - deletes old statuses from fediverse accounts. This tool was previously
called MastodonAmnesia
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
import asyncio
import json
import logging
import sys
from math import ceil
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import aiohttp
import arrow
import click
from aiohttp.client_exceptions import ClientError
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ActivityPubError
from minimal_activitypub.client_2_server import RatelimitError
from rich import print
from rich import traceback
from tqdm import tqdm
from tqdm import trange

from . import Status
from . import __display_name__
from . import __version__
from .config import setup_shop
from .util import AuditLog
from .util import check_updates
from .util import should_keep

traceback.install(show_locals=True)
logger = logging.getLogger(__display_name__)
logger.setLevel(logging.DEBUG)


async def main(  # noqa: max-complexity: 13
    config_file: str,
    is_dry_run: bool,
    debug_log_file: Optional[str],
    audit_log_file: Optional[str],
    audit_log_style: Optional[str],
    batch_size: Optional[int],
    limit: Optional[int],
) -> None:
    """Perform app function."""
    config = await setup_shop(
        config_file=config_file,
        debug_log_file=debug_log_file,
    )

    oldest_to_keep = arrow.now().shift(seconds=-config.bot.delete_after)

    print(f"Welcome to {__display_name__} {__version__}")
    logger.debug("main -Welcome to %s %s", __display_name__, __version__)

    check_updates()

    try:
        session = aiohttp.ClientSession()

        instance = ActivityPub(
            instance=config.mastodon.instance,
            access_token=config.mastodon.access_token,
            session=session,
        )
        await instance.determine_instance_type()
        user_info = await instance.verify_credentials()
        print(
            f"We are removing statuses older than {oldest_to_keep} "
            f"from {config.mastodon.instance}@{user_info['username']}"
        )

        audit_log = None
        if audit_log_file:
            print(
                f"A record of all deleted statuses will be recorded in the audit log file at {audit_log_file}"
            )
            audit_log = await AuditLog.open(
                audit_log_file=audit_log_file,
                style=audit_log_style,
            )

        statuses = await instance.get_account_statuses(account_id=user_info["id"])
    except RatelimitError:
        print(
            f"RateLimited during startup, [red]Please wait until[/red] "
            f"{instance.ratelimit_reset} before trying again"
        )
        sys.exit(429)
    except (ClientError, ActivityPubError):
        logger.exception("!!! Cannot continue.")
        sys.exit(100)

    statuses_to_delete: List[Status] = []
    title = "Finding statuses to delete"
    progress_bar = tqdm(
        desc=f"{title:.<60}",
        ncols=120,
        unit="statuses",
        position=0,
        bar_format="{l_bar} {n_fmt} at {rate_fmt}",
    )
    while True:
        try:
            for status in statuses:
                logger.debug(
                    "Processing status: %s from %s",
                    status.get("url"),
                    arrow.get(status.get("created_at")).to(tz="local"),
                )
                logger.debug(
                    "Oldest to keep vs status created at %s > %s",
                    oldest_to_keep,
                    arrow.get(status.get("created_at")).to(tz="local"),
                )

                if should_keep(
                    status=status,
                    oldest_to_keep=oldest_to_keep,
                    config=config,
                ):
                    logger.info(
                        "Not deleting status: "
                        "Bookmarked: %s - "
                        "My Fav: %s - "
                        "Pinned: %s - "
                        "Poll: %s - "
                        "Attachements: %s - "
                        "Faved: %s - "
                        "Boosted: %s - "
                        "DM: %s -+- "
                        "Created At: %s -+- "
                        "%s",
                        status.get("bookmarked"),
                        status.get("favourited"),
                        status.get("pinned"),
                        (status.get("poll") is not None),
                        len(status.get("media_attachments")),
                        status.get("favourites_count"),
                        status.get("reblogs_count"),
                        (status.get("visibility") == "direct"),
                        arrow.get(status.get("created_at")).to(tz="local"),
                        status.get("url"),
                    )

                elif limit and len(statuses_to_delete) >= limit:
                    break

                else:
                    statuses_to_delete.append(status)

                progress_bar.update()

            if limit and len(statuses_to_delete) >= limit:
                break

            # Get More statuses if available:
            logger.debug("Main - get next batch of statuses if available.")
            logger.debug("Main - instance.pagination: %s", instance.pagination)
            if (
                instance.pagination["next"]["max_id"]
                or instance.pagination["next"]["min_id"]
            ):
                statuses = await instance.get_account_statuses(
                    account_id=user_info["id"],
                    max_id=instance.pagination["next"]["max_id"],
                    min_id=instance.pagination["next"]["min_id"],
                )
                logger.debug("Main - scrolling - len(statuses): %s", len(statuses))
                if len(statuses) == 0:
                    break
            else:
                break

        except RatelimitError:
            await sleep_off_ratelimiting(instance=instance)

    progress_bar.close()

    total_statuses_to_delete = len(statuses_to_delete)
    logger.debug(
        "Main - start deleting - total_statuses_to_delete: %s", total_statuses_to_delete
    )
    for status in statuses_to_delete:
        logger.debug(
            "Start of deleting - status to delete: %s @ %s",
            status["id"],
            status["url"],
        )

    # If dry-run has been specified, print out list of statuses that would be deleted
    if is_dry_run:
        print("\n--dry-run or -d specified. [yellow][bold]No statuses will be deleted")
        for status in statuses_to_delete:
            print(
                f"[red]Would[/red] delete status"
                f" {status.get('url')} from {status.get('created_at')}"
            )
        print(f"Total of {total_statuses_to_delete} statuses would be deleted.")

    # Dry-run has not been specified... delete statuses!
    else:
        await delete_statuses(
            instance=instance,
            statuses_to_delete=statuses_to_delete,
            audit=audit_log,
            batch_size=batch_size,
        )
        print(
            f"All old statuses deleted! Total of {total_statuses_to_delete} statuses deleted"
        )

    if audit_log:
        await audit_log.close()
    await session.close()


async def delete_statuses(
    instance: ActivityPub,
    statuses_to_delete: List[Status],
    audit: Optional[AuditLog],
    batch_size: Optional[int],
) -> None:
    """Delete all statuses that should be deleted."""
    title = "Deleting statuses"
    total_statuses_to_delete = len(statuses_to_delete)
    if total_statuses_to_delete > 0:
        with tqdm(
            desc=f"{title:.<60}",
            ncols=120,
            total=total_statuses_to_delete,
            unit="statuses",
            position=0,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} at {rate_fmt}",
        ) as progress_bar:
            while len(statuses_to_delete) > 0:
                tasks = []
                for status in statuses_to_delete:
                    tasks.append(
                        delete_single_status(
                            status=status, instance=instance, audit=audit
                        )
                    )
                    if batch_size and len(tasks) >= batch_size:
                        break

                responses = await asyncio.gather(*tasks)

                # Filter out any responses that are None...
                # Those encountered Rate Limiting
                deleted_statuses = [
                    status for status in responses if status is not None
                ]
                logger.debug(
                    "delete_statuses - len(deleted_statuses): %s",
                    len(deleted_statuses),
                )

                progress_bar.update(len(deleted_statuses))

                if len(deleted_statuses) < len(statuses_to_delete):
                    await sleep_off_ratelimiting(instance=instance)

                for status in deleted_statuses:
                    statuses_to_delete.remove(status)


async def sleep_off_ratelimiting(
    instance: ActivityPub,
) -> None:
    """Wait for rate limiting to be over."""
    logger.debug(
        "sleep_off_ratelimiting - Rate limited: Limit: %s - resetting at: %s",
        instance.ratelimit_remaining,
        instance.ratelimit_reset,
    )
    reset_at = arrow.get(instance.ratelimit_reset).datetime
    now = arrow.now().datetime
    need_to_wait = ceil((reset_at - now).total_seconds())

    logger.info(
        "Need to wait %s seconds (until %s) to let server 'cool down'",
        need_to_wait,
        arrow.get(instance.ratelimit_reset),
    )
    bar_title = "Waiting to let server 'cool-down'"
    for _i in trange(
        need_to_wait,
        desc=f"{bar_title:.<60}",
        unit="s",
        ncols=120,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| Eta: {remaining} - Elapsed: {elapsed}",
        position=1,
    ):
        await asyncio.sleep(1)


async def delete_single_status(
    status: Status,
    instance: ActivityPub,
    audit: Optional[AuditLog],
) -> Optional[Dict[str, Any]]:
    """Delete  single status."""
    logger.debug(
        "delete_single_status(status=%s, instance=%s)",
        status["id"],
        instance.instance,
    )
    return_status: Optional[Status] = status
    try:
        await instance.delete_status(status=status)
        logger.info(
            "delete_single_status - Deleted status %s from %s",
            status.get("url"),
            status.get("created_at"),
        )
        if audit:
            await audit.add_entry(status=status)
    except RatelimitError:
        logger.debug(
            "delete_single_status - status id = %s - ratelimit_remaining = %s - ratelimit_reset = %s",
            status["id"],
            instance.ratelimit_remaining,
            instance.ratelimit_reset,
        )
        return_status = None
    except ActivityPubError as error:
        logger.debug(
            "delete_single_status - encountered error: %s",
            error,
        )
        logger.debug("delete_single_status - status: %s", json.dumps(status, indent=4))
        raise error

    return return_status


@click.command()
@click.option(
    "-c",
    "--config-file",
    help="Name of configuration file to use",
    default="config.json",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
)
@click.option(
    "-d",
    "--dry-run",
    help="Only print out which statuses would be deleted. No actual deletion occurs",
    is_flag=True,
)
@click.option(
    "--debug-log-file",
    help="Path of filename to save DEBUG log messages to",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
)
@click.option(
    "-a",
    "--audit-log-file",
    help="Path of filename to save audit log to",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
)
@click.option(
    "--audit-log-style",
    help="Style to use for audit log entries",
    type=click.Choice([style.name for style in AuditLog.Style]),
    default=AuditLog.Style.PLAIN.name,
)
@click.option(
    "-b",
    "--batch-size",
    help="How many deletes to process in one batch",
    type=click.INT,
)
@click.option(
    "-l",
    "--limit",
    help="Maximum number of of deletes to process",
    type=click.INT,
)
def start(  # noqa: PLR0913
    config_file: str,
    dry_run: bool,
    debug_log_file: Optional[str],
    audit_log_file: Optional[str],
    audit_log_style: Optional[str],
    batch_size: Optional[int],
    limit: Optional[int],
) -> None:
    """Start app."""
    asyncio.run(
        main(
            config_file=config_file,
            is_dry_run=dry_run,
            debug_log_file=debug_log_file,
            audit_log_file=audit_log_file,
            audit_log_style=audit_log_style,
            batch_size=batch_size,
            limit=limit,
        )
    )
