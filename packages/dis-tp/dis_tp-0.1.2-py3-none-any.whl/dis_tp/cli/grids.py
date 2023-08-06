import pathlib

import click

from .. import Initialize
from .. import MatchingFunc as mcf
from .. import ReadTxt
from .. import TildeCoeffFunc as tcf
from .. import parameters
from .base import command, root_path


@command.group("grids")
def subcommand():
    """Generate grids"""


heavy_id = click.argument("h_id", type=int)

pto = click.argument("PTO", type=int)

flavor_entry = click.argument(
    "flavor_entry",
    type=str,
)

n_cores = click.option(
    "-n",
    "--n_cores",
    type=int,
    default=4,
    required=False,
    help="Number of cores",
)

dest_path = click.option(
    "-d",
    "--dest_path",
    type=pathlib.Path,
    default=root_path,
    required=False,
    help="destination path",
)


@subcommand.command("matching")
@heavy_id
@flavor_entry
@pto
@n_cores
@dest_path
def generate_matching_grids(
    h_id: int, flavor_entry: str, pto: int, n_cores: int, dest_path: pathlib.Path
):
    """Construct matching grids."""

    if pto == 3:
        if flavor_entry == "bq":
            func = mcf.Mbq_3_reg
        elif flavor_entry == "bg":
            func = mcf.Mbg_3_reg
    path = dest_path / f"M{flavor_entry}_{pto}/M{flavor_entry}{pto}_nf{h_id}.txt"
    Initialize.Initialize_all(h_id)
    parameters.initialize_theory(use_grids=True)
    obj = ReadTxt.Construct_Grid(
        func, h_id=h_id, path=path, grid_type="matching", n_pools=n_cores
    )
    obj.run()


@subcommand.command("tilde")
@heavy_id
@flavor_entry
@pto
@n_cores
@click.option(
    "-v",
    "--n3lo_variation",
    type=int,
    default=0,
    required=False,
    help="N3LO coeffieicnt variation",
)
@dest_path
def generate_matching_grids(
    h_id: int,
    flavor_entry: str,
    pto: int,
    n_cores: int,
    n3lo_variation: int,
    dest_path: pathlib.Path,
):
    """Construct tilde grids."""
    flavor = flavor_entry[-1] if "2" in flavor_entry else flavor_entry

    if pto == 3:
        if flavor_entry == "2q":
            func = tcf.Cq_3_til_reg
        elif flavor_entry == "2g":
            func = tcf.Cg_3_til_reg
        elif flavor_entry == "Lq":
            func = tcf.CLq_3_til_reg
        elif flavor_entry == "Lg":
            func = tcf.CLg_3_til_reg

    path = (
        dest_path
        / f"C{flavor}_{pto}_til/C{flavor}{pto}til_nf{h_id}_var{n3lo_variation}.txt"
    )
    Initialize.Initialize_all(h_id, n3lo_variation)
    parameters.initialize_theory(use_grids=True)
    obj = ReadTxt.Construct_Grid(
        func, h_id=h_id, path=path, grid_type="tilde", n_pools=n_cores
    )
    obj.run()
