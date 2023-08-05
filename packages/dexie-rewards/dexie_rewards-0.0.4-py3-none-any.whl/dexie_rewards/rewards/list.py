import asyncio
from io import StringIO
import json
import rich_click as click

from rich.console import Console

from typing import Optional

from ..services.dexie_db import create_db
from ..types.offer_reward import OfferReward
from ..utils import wait_for_synced_wallet
from .utils import display_rewards, get_offers_with_claimable_rewards

console = Console()


@click.command("list", short_help="List all offers with dexie rewards")
@click.option(
    "-f",
    "--fingerprint",
    required=False,
    help="Set the fingerprint to specify which wallet to use",
    type=int,
)
@click.option(
    "-j",
    "--json",
    "as_json",
    help="Displays offers as JSON",
    is_flag=True,
    default=False,
    show_default=True,
)
def list_cmds(fingerprint: Optional[int], as_json: bool) -> None:
    asyncio.run(list_cmds_async(fingerprint, as_json))


async def list_cmds_async(fingerprint: Optional[int], as_json: bool) -> None:
    console = Console(file=StringIO()) if as_json else Console()

    synced_fingerprint = await wait_for_synced_wallet(fingerprint, console)
    await create_db(synced_fingerprint)

    offers_rewards_dict = await get_offers_with_claimable_rewards(
        synced_fingerprint, console
    )
    if as_json:
        click.echo(json.dumps(offers_rewards_dict))
    else:
        offers_rewards = list(map(OfferReward.from_json_dict, offers_rewards_dict))
        display_rewards(offers_rewards)
