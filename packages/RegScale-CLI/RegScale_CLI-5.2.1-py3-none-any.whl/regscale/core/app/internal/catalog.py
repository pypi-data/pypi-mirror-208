#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates catalog export, diagnose and compare into RegScale"""

# standard python imports
import click

from regscale.core.app.utils.catalog_utils.compare_catalog import (
    display_menu as start_compare,
)
from regscale.core.app.utils.catalog_utils.diagnostic_catalog import (
    display_menu as start_diagnostic,
)
from regscale.core.app.utils.catalog_utils.export_catalog import (
    display_menu as start_export,
)


@click.group()
def catalog():
    """Export, diagnose, and compare catalog from RegScale.com/regulations."""


@catalog.command(name="export")
def export():
    """Export catalog from RegScale.com/regulations."""
    start_export()


@catalog.command(name="diagnose")
def diagnostic():
    """Diagnose catalog and output metadata."""
    start_diagnostic()


@catalog.command(name="compare")
def compare():
    """Run diagnostic and compare catalogs while reporting differences."""
    start_compare()
