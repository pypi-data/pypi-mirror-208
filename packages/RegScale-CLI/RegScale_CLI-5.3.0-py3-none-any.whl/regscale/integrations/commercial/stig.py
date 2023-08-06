#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

"""STIG CLI"""

import datetime
import os
import re
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from json import JSONDecodeError, dump, dumps, load
from pathlib import Path
from subprocess import CalledProcessError, run
from threading import Thread, get_native_id
from typing import Tuple

import click
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_license,
    convert_datetime_to_regscale_string,
    copy_and_overwrite,
    create_progress_object,
    download_file,
    format_data_to_html,
    get_current_datetime,
    get_site_package_location,
    random_hex_color,
    xml_file_to_dict,
)
from regscale.models.regscale_models import Component, ControlImplementation
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.checklist import Checklist
from regscale.models.regscale_models.implementation_objective import (
    ImplementationObjective,
)
from regscale.models.regscale_models.implementation_option import ImplementationOption
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.stig import STIG_FILE
from regscale.validation.address import validate_mac_address

logger = create_logger(propagate=True)
update_objective_progress = create_progress_object()
insert_objective_progress = create_progress_object()
ssp_implementation_progress = create_progress_object()

all_rules = []
all_platform_objectives = []


@click.group()
def stig():
    """Performs STIG processing operations"""
    check_license()


@stig.command()
def update_cci_mapping():
    """Update the DISA CCI Mapping files (requires internet connection)"""
    cci_control_mapping(force=True)


@stig.command()
@click.option(
    "--folder_path",
    prompt="Enter the folder path of the STIGs to process",
    help="RegScale will process and load the STIGs",
    type=click.Path(exists=True),
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    required=True,
    help="Enter RegScale SSP id",
)
def process_stig(folder_path: click.Path, regscale_ssp_id: click.INT):
    """Parse CKL Files from a given folder and Create RegScale Issues"""
    STIG(
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        cci_mapping=cci_control_mapping(),
    )


def check_powershell(app: Application):
    """Check if powershell is installed

    :param app: Application instance
    """
    if (
        "not found".lower() in app.get_pwsh()
        or not Path(app.config["pwshPath"]).exists()
    ):
        logger.error(
            "Powershell not found, please check init.yaml and add the full powershell path."
        )
        sys.exit(1)


def check_scripts(app: Application):
    """Check if iterate scripts folder exists, and if not download scripts

    :param app: Application instance
    """
    config = app.config
    site_path = get_site_package_location()
    if not Path(config["stig_script_path"]).exists():
        logger.info(
            "Iterate scripts not found, copying iterate script folder from \
                site packages to current working directory!"
        )
        try:
            copy_and_overwrite(
                Path(str(site_path.absolute()) + os.sep + "iterate"),
                Path(config["stig_script_path"]),
            )
            logger.info("STIG Iterate scripts copied, please re-run your command")
            sys.exit(0)

        except FileNotFoundError as fex:
            logger.error("Unable to find file path\n%s", fex)
            sys.exit(1)


def command_str(script_path: Path, *args) -> None:
    """Powershell command

    :param script_path: The script path
    :return: None
    """
    app = Application()
    config = app.config
    check_powershell(app)
    check_scripts(app)
    pwsh_path = config["pwshPath"]
    command = [
        pwsh_path,
        Path(config["stig_script_path"]) / script_path,
    ]
    if args:
        command.append([" ".join([str(item) for item in args])])
    logger.info(
        "Executing Powershell... %s",
        [" ".join([str(item) for item in command])],
    )
    try:
        run(command, shell=False, check=True)
    except CalledProcessError as ex:
        if "status 3" not in str(ex):
            logger.error("CalledProcessError: %s", ex)


def update_mapping() -> dict:
    """Convert CCI source mapping to friendly dictionary format

    :return: A dictionary of CCI mappings
    """
    data_ctl = {}
    data_cci = {}
    html_doc = "U_CCI_List.html"  # 'nistvscci.html' # "NIST 800-53 Analysis.html"
    with open(Path("./assets") / html_doc, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    for resultset in [tag.select("tr") for tag in soup.select("table")[1:]]:  # tbody
        # type(resultset)
        # type(innertag)
        # innertag

        # ctl_id 'AC-1 a 1'
        # cci_id: 'CCI-000001'
        # Filter on NIST SP 800-53 Revision 4 (v4)
        revision = "NIST SP 800-53 Revision 4 (v4)"
        dat = {
            tag.select("td")[1].get_text().split(":")[2].strip()
            for tag in resultset
            if revision in tag.select("td")[1].get_text()
        }
        try:
            if dat:
                ctl_id = dat.pop()
                cci_id = resultset[0].select("td")[1].get_text()
                ctl_id_parse = re.match(r"^([A-Z][A-Z]-[0-9])(.*)", ctl_id)
                ctl_id_main = ctl_id_parse.group(1)
                ctl_id_parts = ctl_id_parse.group(2).lstrip(" ").replace(" ", ".")
                ctl_id_v1 = f"{ctl_id_main}{ctl_id_parts}"
                ctl_id_oscal = f"{ctl_id_main.lower()}{ctl_id_parts.lower()}"
                cci_text = resultset[2].select("td")[1].get_text()
                # Build custom dicts
                data_dict = {
                    "ctl_id": ctl_id,
                    "ctl_id_main": ctl_id_main,
                    "ctl_id_parts": ctl_id_parts,
                    "ctl_id_v1": ctl_id_v1,
                    "ctl_id_oscal": ctl_id_oscal,
                    "cci_id": cci_id,
                    "cci_text": cci_text,
                }
                if ctl_id in data_ctl:
                    data_ctl[ctl_id].append(data_dict)
                else:
                    data_ctl[ctl_id] = [data_dict]
                if cci_id in data_cci:
                    data_cci[cci_id].append(data_dict)
                else:
                    data_cci[cci_id] = [data_dict]
        except Exception as ex:
            logger.error(ex)

    # Check for missing CCIs from reference
    auth_ref_spreadsheet = "stig-mapping-to-nist-800-53.xlsx"
    file_name = os.path.join("assets", auth_ref_spreadsheet)
    df_dict = pd.read_excel(file_name, header=1)
    nist_cci_to_ctl_map = {}
    for _, row in df_dict.iterrows():
        # Skip blank CTL rows for CCI in the NIST spreadsheet
        if isinstance(row.get("index"), float):
            continue
        cci_id = row.get("CCI", "")
        ctl_id = row.get("index", "")
        try:
            ctl_id_parse = re.match(r"^([A-Z][A-Z]-[0-9])(.*)", ctl_id)
            ctl_id_main = ctl_id_parse.group(1)
            ctl_id_parts = ctl_id_parse.group(2).lstrip(" ").replace(" ", ".")
            ctl_id_v1 = f"{ctl_id_main}{ctl_id_parts}"
            ctl_id_oscal = f"{ctl_id_main.lower()}{ctl_id_parts.lower()}"
        except AttributeError:
            ctl_id_parse = "missing"
            ctl_id_main = "missing"
            ctl_id_parts = "missing"
            ctl_id_v1 = "missing"
            ctl_id_oscal = "missing"
        cci_text = row.get("/cci_items/cci_item/definition", "")
        contributor = row.get("contributor", "")
        item = row.get("Item", "")
        row_dict = {
            "ctl_id": ctl_id,
            "ctl_id_main": ctl_id_main,
            "ctl_id_parts": ctl_id_parts,
            "ctl_id_v1": ctl_id_v1,
            "ctl_id_oscal": ctl_id_oscal,
            "cci_id": cci_id,
            "cci_text": cci_text,
            "contributor": contributor,
            "item": item,
        }
        if cci_id in nist_cci_to_ctl_map:
            nist_cci_to_ctl_map[cci_id].append(row_dict)
        else:
            nist_cci_to_ctl_map[cci_id] = [row_dict]

    # Add missing CCIs to maps
    auth_cci_list = nist_cci_to_ctl_map.keys()
    missing_cci = []
    for cci_id in auth_cci_list:
        if cci_id in data_cci:
            pass
        else:
            logger.debug("cci_id %s not found in data_cci", cci_id)
            # print(nist_cci_to_ctl_map[cci_id])
            missing_cci.append(cci_id)
            # Add missing cci to data_cci
            data_cci[cci_id] = nist_cci_to_ctl_map[cci_id]

    # update json files
    with open(Path("assets") / "data_cci.json", "w+", encoding="utf-8") as file:
        logger.info("Updating %s...", (Path("assets") / "data_cci.json").resolve())
        dump(data_cci, file)

    return data_cci


def cci_control_mapping(save_path="./assets/U_CCI_List.html", force=False) -> dict:
    """Pull CCI Controls from DOD source, saved to assets.

    :param save_path: The save path of the file, defaults to "./assets/U_CCI_List.html"
    :param force: Force a rebuild, even if file exists, defaults to False
    :return: A dictionary of the CCI to Control mapping.
    """
    # https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CCI_List.zip
    if not Path(save_path).parent.exists():
        os.mkdir(Path(save_path).parent)
    dl_path = tempfile.gettempdir() + os.sep + "U_CCI_List.html"
    xl_path = Path(save_path).parent / "stig-mapping-to-nist-800-53.xlsx"
    if not xl_path.exists() or force:
        # download cci html file
        mapping_url = "https://csrc.nist.gov/csrc/media/projects/forum/documents/stig-mapping-to-nist-800-53.xlsx"
        xl_path.touch()
        download_file(url=mapping_url, download_path=str(Path(save_path).parent))
    if not Path(save_path).exists() or force:
        url = "https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_CCI_List.zip"
        # download cci html file
        file = download_file(url=url, download_path=tempfile.gettempdir(), verify=False)
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())
            shutil.copy(dl_path, save_path)
    if not (Path("assets") / "data_cci.json").exists() or force:
        mapping = update_mapping()
    else:
        with open((Path("assets") / "data_cci.json"), encoding="utf-8") as json_file:
            mapping = load(json_file)
    return mapping


class STIG:
    """A class to process STIG files"""

    def __init__(self, folder_path, regscale_ssp_id, cci_mapping=None):
        stig_logger = create_logger(propagate=True)
        app = Application()
        config = app.config
        api = Api(app)
        self.config = config
        self.cci_mapping = cci_mapping
        self.logger = stig_logger
        self.app = app
        self.api = api
        self.folder_path = folder_path
        self.regscale_ssp = regscale_ssp_id
        self.files = list(Path(folder_path).glob("*.ckl"))
        self.ssp_issues = []
        self.all_security_checklists = []
        self.process(regscale_ssp_id=regscale_ssp_id)
        self.final_check()

    def final_check(self) -> None:
        """
        Assert that all objectives no longer have failed implementations
            Solves probable race conditions in "process"
        :return: None
        """
        # if any name from all rules is in the notes from all objectives, the objective fails

        objs_to_update = []
        for rule in all_rules:
            for obj in all_platform_objectives:
                if rule["STIGRef"] in obj["notes"]:
                    if rule["STIGRef"] + str(obj["id"]) not in {
                        u_obj["rule"] + str(u_obj["obj"]["id"])
                        for u_obj in objs_to_update
                    }:
                        objs_to_update.append({"rule": rule["STIGRef"], "obj": obj})
        if objs_to_update:
            for obj in objs_to_update:
                objective_id = obj["obj"]["id"]
                implementation_id = obj["obj"]["implementationId"]
                existing_implementation = self.api.get(
                    url=self.config["domain"]
                    + f"/api/controlimplementation/{implementation_id}",
                ).json()

                # Get Full Objective
                existing_obj = [
                    obj
                    for obj in existing_implementation["objectives"]
                    if obj["id"] == objective_id
                ][0]
                if (
                    "status" not in existing_obj
                    or existing_obj["status"] != "Not Implemented"
                ):
                    existing_obj["status"] = "Not Implemented"
                    del existing_obj[
                        "implementation"
                    ]  # don't need this data for a put, this won't affect the database.
                    response = ImplementationObjective.update_objective(
                        app=self.app, obj=existing_obj
                    )
                    if not response.ok:
                        self.logger.error(
                            "Unable to update Objective: %s", existing_obj
                        )
                    self.update_implementation(
                        existing_imp=existing_implementation,
                        status=existing_obj["status"],
                    )

    def get_checklists_by_implementation(self, implementation: dict) -> list:
        """
        Get all checklists for a given implementation
        :param implementation: Dictionary of implementation
        :return: List of checklists
        :rtype: list
        """
        checklists = []
        assets = self.api.get(
            url=self.config["domain"]
            + f"/api/assets/getAllByParent/{implementation['parentId']}/components"
        ).json()
        for asset in assets:
            checklists.extend(
                self.api.get(
                    url=self.config["domain"]
                    + f"/api/securityChecklist/getAllByParent/{asset['id']}"
                ).json()
            )
        return checklists

    def lookup_cci_status(self, cci: str, all_checklists: list[dict]) -> str:
        """
        A simple lookup to determine status from all the checklists with a given CCI
        :param str cci: CCI identifier
        :param list[dict] all_checklists: A list of all checklists
        :return: Checklist status
        :rtype: str
        """
        status = "Fail"
        results = {chk["status"] for chk in all_checklists if chk["cci"] == cci}
        c = Counter(results)
        self.logger.debug("Counter: %s", c)
        if "Pass" in c and c.total() == 1:
            status = "Pass"
        return status

    def refresh_component_implementations(self, component_ids: list[int]) -> list[dict]:
        """
        Return all existing component implementations for a list of component ids
        :param component_ids: list of component ids
        :return: list of component implementations
        :rtype: list[dict]
        """
        url = self.config["domain"] + "/api/controlimplementation"
        all_existing_component_implementations = []
        for component_id in component_ids:
            existing_component_implementations = []
            existing_component_response = self.api.get(
                url=url + f"/getAllByParent/{component_id}/components"
            )
            if existing_component_response.ok:
                existing_component_implementations = existing_component_response.json()
                all_existing_component_implementations.extend(
                    existing_component_implementations
                )
        return all_existing_component_implementations

    def build_implementations(
        self, existing_assets: list[dict], cci_list: list[str], cat_id: int
    ) -> Tuple[list[dict], list[dict]]:
        """Build a list of new implementations and a list of new objectives

        :param list[dict] existing_assets: A list of assets
        :param list[str] cci_list: A list of CCIs
        :param int cat_id: A catalog id
        :return: A tuple of new implementations and new objectives
        :rtype: Tuple[list[dict], list[dict]]
        """
        control_implementations = []
        control_objectives = []
        url = self.config["domain"] + "/api/controlimplementation"
        new_imps = set()
        component_ids = {asset["parentId"] for asset in existing_assets}
        # ssp_implementations = self.api.get(url=url + f"/getAllByPlan/{ssp_id}").json()
        # security_control_ids = {imp["controlID"] for imp in ssp_implementations}
        control_objectives.extend(
            self.api.get(
                url=self.config["domain"]
                + f"/api/controlobjectives/getByCatalog/{cat_id}"
            ).json()
        )
        all_existing_component_implementations = self.refresh_component_implementations(
            component_ids=component_ids
        )
        # Lookup CCI
        for cci in cci_list:
            try:
                security_control_id = [
                    obj["securityControlId"]
                    for obj in control_objectives
                    if obj["name"] == cci
                ][0]
            except IndexError:
                self.logger.error(
                    "Unable to find %s in base catalog (#%i).", cci, cat_id
                )
                continue
            for component_id in component_ids:
                if security_control_id not in {
                    imp["controlID"]
                    for imp in all_existing_component_implementations
                    if imp["parentId"] == component_id
                }:
                    control_implementation = ControlImplementation(
                        parentId=component_id,  # Should be only a single asset
                        parentModule="components",
                        controlOwnerId=self.config["userId"],
                        status="Not Implemented",
                        controlID=security_control_id,
                    )
                    new_imps.add(control_implementation)
        if new_imps:
            response = self.api.post(
                url=url + "/batchcreate", json=[asdict(imp) for imp in new_imps]
            )
            if not response.raise_for_status():
                control_implementations = response.json()
        else:
            control_implementations = all_existing_component_implementations
        return control_objectives, control_implementations

    def send_objective_insert_or_update(
        self, url: str, imp_obj: dict, action_type: str = "update"
    ) -> requests.Response:
        """
        Function for updating or inserting objectives to RegScale via API
        :param str url: URL for API call
        :param dict imp_obj: Dictionary of implementation objective
        :param str action_type: method type for API method, default is update
        :return: API response object
        :rtype: requests.Response
        """
        imp_obj_id = imp_obj["id"]
        if action_type == "update":
            response = (
                self.api.put(url=url + f"/{imp_obj_id}", json=imp_obj)
                if imp_obj_id
                else requests.Response()
            )
        else:
            response = self.api.post(url=url, json=imp_obj)
        return response

    def create_objectives(
        self,
        implementation: dict,
        options: list[dict],
        control_objectives: list[dict],
        all_checklists: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """
        Create objectives for a given implementation
        :param dict implementation: Dictionary of implementation object to create objectives for
        :param list[dict] options: Options for the implementation
        :param list[dict] control_objectives: Objectives for the implementation
        :param list[dict] all_checklists: checklists for the implementation
        :return: two lists of implementation objectives, one for inserts and one for updates
        :rtype: tuple[list[dict], list[dict]]
        """
        insert_objs = []
        update_objs = []
        existing_objectives = ImplementationObjective.fetch_implementation_objectives(
            self.app, implementation["id"]
        )
        if not options:
            raise ValueError(
                f"Unable to fetch options for implementation #{implementation['id']}"
            )

        self.logger.debug(
            "Updating or creating %i implementation objectives for implementation # %i",
            len(control_objectives),
            implementation["id"],
        )
        for obj in control_objectives:
            status = self.lookup_cci_status(
                cci=obj["name"], all_checklists=all_checklists
            )
            opts = [opt for opt in options if opt["objectiveId"] == obj["id"]]
            key = "Fully Implemented" if status == "Pass" else "Not Implemented"
            option_id = [opt["id"] for opt in opts if opt["description"] == key][0]
            imp_obj = ImplementationObjective(
                id=0,
                uuid="",
                implementationId=implementation["id"],
                status=key,
                objectiveId=obj["id"],
                optionId=option_id,
                notes=obj["name"],
                securityControlId=obj["securityControlId"],
            )
            if imp_obj.notes not in {obj["notes"] for obj in existing_objectives}:
                insert_objs.append(asdict(imp_obj))
            else:
                match_obj = {
                    obj["id"]
                    for obj in existing_objectives
                    if imp_obj.notes == obj["notes"]
                    and obj["implementationId"] == imp_obj.implementationId
                }
                if match_obj:
                    imp_obj.id = match_obj.pop()
                    update_objs.append(asdict(imp_obj))
        return insert_objs, update_objs

    def mass_update(self, update_objs: list[dict], insert_objs: list[dict]) -> None:
        """
        Function to update and insert objectives in batches to RegScale via API
        :param list[dict] update_objs: List of implementation objectives to update
        :param list[dict] insert_objs: List of implementation objectives to create
        :return: None
        """
        url = self.config["domain"] + "/api/implementationobjectives"
        self.logger.debug("Insert Objectives: %i", len(insert_objs))
        self.logger.debug("Update Objectives: %i", len(update_objs))
        n_threads = 100  # Keep this constrained

        def update(objs, progress, method="insert"):
            with progress:
                objectives = progress.add_task(
                    f"[{random_hex_color()}]{method.title()} {len(objs)} implementation objectives at the component level...",
                    total=len(objs),
                )
                with ThreadPoolExecutor(max_workers=n_threads) as pool:
                    # Prone to race conditions on inserting new items with a lack of FK/Unique contraints, be careful
                    # Process each file
                    lst = [
                        pool.submit(
                            self.send_objective_insert_or_update,
                            url,
                            imp_obj,
                            action_type=method,
                        )
                        for imp_obj in objs
                    ]
                    for _ in as_completed(lst):
                        progress.update(objectives, advance=1)

        update(objs=insert_objs, progress=insert_objective_progress, method="insert")
        update(objs=update_objs, progress=update_objective_progress, method="update")

    def get_all_component_implementations(self) -> list[dict]:
        """
        Get all Component Implementations
        :return: A list of all Component Implementations
        :rtype: list[dict]
        """
        existing_components = self.check_components()
        control_implementations = []
        for component in existing_components:
            control_implementations.extend(
                self.get_implementations(
                    parent_id=component["id"], parent_module="components"
                )
            )
            self.all_security_checklists.extend(
                Checklist.get_checklists(
                    parent_id=component["id"], parent_module="components"
                )
            )

        return control_implementations

    def update_component_implementations(self) -> None:
        """
        Update Component Implementations
        :return: None
        """
        control_implementations = self.get_all_component_implementations()
        self.logger.info(
            "Updating %i Component Implementations", len(control_implementations)
        )
        # Update implementations
        for control in control_implementations:
            objective_status = "Not Implemented"
            sec_control_objectives = (
                ImplementationObjective.fetch_implementation_objectives(
                    app=self.app, control_id=control["controlID"], query_type="control"
                )["implementationObjectives"]["items"]
            )
            objectives = [
                obj
                for obj in sec_control_objectives
                if obj["implementationId"] == control["id"]
            ]
            if objectives:
                cntr = Counter([obj["status"] for obj in objectives])
                if cntr["Fully Implemented"] == cntr.total():
                    objective_status = "Fully Implemented"
                if control["status"] != objective_status:
                    control["status"] = objective_status
                    self.api.put(
                        url=self.config["domain"]
                        + f"/api/controlImplementation/{control['id']}",
                        json=control,
                    )

    def _create_issue(self, issue: dict) -> list:
        """
        Create an issue in RegScale via API
        :param dict issue: Issue object to create in RegScale via API
        :return: JSON response from RegScale API
        :rtype: list
        """
        r = self.api.post(self.app.config["domain"] + "/api/issues", json=issue)
        if r.status_code == 200:
            self.logger.info("Created issue: %s - #%i", issue["title"], r.json()["id"])
            self.logger.debug(r.json())
        return r.json()

    def _update_issue(self, issue: dict) -> list:
        """
        Update an issue in RegScale via API
        :param dict issue: Issue object to update in RegScale via API
        :return: JSON response from RegScale API
        :rtype: list
        """
        r = self.api.put(
            self.app.config["domain"] + f"/api/issues/{issue['id']}", json=issue
        )
        if r.status_code == 200:
            self.logger.info("Updated issue: %s - #%i", issue["title"], issue["id"])
            self.logger.debug(r.json())
        return r.json()

    def update_ssp_issues(self) -> None:
        """
        Create or update issues for failed SSP control implementations
        :return: None
        """
        control_implementations = self.get_all_component_implementations()
        r = self.api.get(
            url=self.config["domain"]
            + f"/api/issues/getAllByParent/{self.regscale_ssp}/securityplans"
        )
        if r.status_code == 200:
            self.ssp_issues = r.json()
        today_date = datetime.date.today().strftime("%m/%d/%y")
        due_date = datetime.datetime.strptime(
            today_date, "%m/%d/%y"
        ) + datetime.timedelta(days=30)
        assets_with_failed_security_checks = {
            (chk["asset"]["name"], chk["asset"]["id"])
            for chk in self.all_security_checklists
            if "asset" in chk and chk["status"] == "Fail"
        }
        assets_with_passed_security_checks = {
            (chk["asset"]["name"], chk["asset"]["id"])
            for chk in self.all_security_checklists
            if "asset" in chk and chk["status"] == "Pass"
        }
        for control in control_implementations:
            description = "No security checklist (STIG) coverage found."
            if assets_with_failed_security_checks:
                description = (
                    f"<p>Assets with failed Security Checks for control: {control['controlName'].upper()}</p>"
                    + "</p>".join(
                        [
                            f"""<p>{asset[0]}: <a href="{self.app.config['domain']}/assets/form/{asset[1]} title="">https://regscale.eatonfam.com/assets/form/{asset[1]}</a>"""
                            for asset in assets_with_failed_security_checks
                        ]
                    )
                )
            elif (
                assets_with_passed_security_checks
                and not assets_with_failed_security_checks
            ):
                description = "No failed security checks found."
            new_issue = Issue(
                title=f"{control['controlName']} is not implemented for component: {control['parentId']}",
                dateCreated=get_current_datetime(),
                status="Open" if control["status"] == "Not Implemented" else "Closed",
                severityLevel="I - High - Significant Deficiency",
                issueOwnerId=self.app.config["userId"],
                securityPlanId=self.regscale_ssp,
                componentId=control["parentId"],
                parentId=self.regscale_ssp,
                parentModule="securityplans",
                identification="STIG Assessment",
                dueDate=convert_datetime_to_regscale_string(due_date),
                description=description,
            )
            # if control["status"] == "Not Implemented":
            match_issue = [
                iss for iss in self.ssp_issues if iss["title"] == new_issue.title
            ]
            if match_issue:
                issue = match_issue[0]
            else:
                issue = asdict(new_issue)
            # Check if issue exists
            if not match_issue and issue["status"] == "Open":
                # Create issue
                self._create_issue(issue)
            else:
                if (new_issue["status"] != issue["status"]) or (
                    new_issue["description"] != issue["description"]
                ):
                    # Update issue
                    issue["status"] = new_issue["status"]
                    del issue["dateCreated"]
                    issue["description"] = new_issue["description"]
                    issue["dateCompleted"] = (
                        get_current_datetime() if issue["status"] == "Closed" else ""
                    )
                    self._update_issue(issue)

    def update_ssp_implementation_objectives(self):
        """Update SSP Implementation Objectives"""

        def process_ssp_objectives(obj):
            fmt = "%Y-%m-%d %H:%M:%S"
            self.logger.debug("Entering Thread: %i", get_native_id())
            if imp["id"] not in (obj["implementationId"] for obj in ssp_objectives):
                # Post
                new_imp_obj = ImplementationObjective(
                    id=0,
                    uuid=None,
                    notes=obj["notes"],
                    optionId=obj["optionId"],  # need to put something here
                    status=obj["status"],
                    dateLastAssessed=datetime.datetime.now().strftime(fmt),
                    objectiveId=obj["objectiveId"],
                    securityControlId=imp["controlID"],
                    implementationId=imp["id"],
                    dateCreated=get_current_datetime(),
                    dateLastUpdated=get_current_datetime(),
                    lastUpdatedById=self.app.config["userId"],
                    createdById=self.app.config["userId"],
                )
                res = ImplementationObjective.insert_objective(
                    app=self.app, obj=new_imp_obj
                )
                if res.status_code != 200:
                    logger.warning("Unable to post new objective: %s", new_imp_obj)
            else:
                # Update
                update_obj = [
                    ssp_obj
                    for ssp_obj in ssp_objectives
                    if obj["objectiveId"] == ssp_obj["objectiveId"]
                ]
                if len(update_obj) > 0 and update_obj[0]["status"] != obj["status"]:
                    update_obj[0]["status"] = obj["status"]
                    res = ImplementationObjective.update_objective(
                        app=self.app, obj=update_obj[0]
                    )
                    if res.status_code != 200:
                        logger.warning("Unable to update objective: %s", update_obj[0])

        component_implementations = []
        existing_components = self.check_components()
        for component in existing_components:
            # Create a list of all component implementations
            component_implementations.extend(
                self.get_implementations(
                    parent_id=component["id"], parent_module="components"
                )
            )
        # Create a list of all SSP implementations
        ssp_control_implementations = self.get_implementations(
            parent_id=self.regscale_ssp, parent_module="securityplans"
        )
        logger.info(
            "Updating %i control implementations for SSP #%i.",
            len(ssp_control_implementations),
            self.regscale_ssp,
        )
        all_implementation_objectives = ImplementationObjective.fetch_all(app=self.app)
        updates = []
        for _, imp in enumerate(ssp_control_implementations):
            component_objectives = []
            ssp_objectives = []
            ssp_implementation_status = "Not Implemented"
            implementation_dat = [
                dat
                for dat in all_implementation_objectives
                if dat["securityControlId"] == imp["controlID"]
            ]
            if implementation_dat:
                ssp_objectives = [
                    item
                    for item in implementation_dat
                    if item["implementationId"]
                    not in (imp["id"] for imp in component_implementations)
                ]
                component_objectives = [
                    item
                    for item in implementation_dat
                    if item["implementationId"]
                    in (imp["id"] for imp in component_implementations)
                ]
            cntr = Counter([obj["status"] for obj in component_objectives])
            if cntr["Fully Implemented"] == cntr.total():
                ssp_implementation_status = "Fully Implemented"
                imp["status"] = ssp_implementation_status

            for obj in component_objectives:
                proc = Thread(target=process_ssp_objectives, args=(obj,))
                proc.start()

            # Update the SSP implementation
            imp["status"] = ssp_implementation_status
            entries_to_remove = ["createdBy", "lastUpdatedBy", "controlOwner"]
            for k in entries_to_remove:
                imp.pop(k, None)
            updates.append(imp)
        count = 0
        size = 50
        update_len = len(updates)
        while len(updates) > 0:
            batch = []
            if len(updates) > 0:
                self.logger.debug(
                    "Updated %i of %i SSP implementations", count, update_len
                )
                batch = updates[:size]
                updates = updates[size:]
                response = self.api.post(
                    url=self.app.config["domain"]
                    + "/api/controlImplementation/batchUpdate",
                    json=batch,
                )
                logger.debug(len(response.json()))
                count += len(batch)
        logger.info("%i SSP implementations updated.", count)

    def update_component_implementation_objectives(
        self, existing_components: list[dict], control_objectives: list[dict]
    ) -> None:
        """
        Update the implementation objectives for each component
        :param list[dict] existing_components: List of existing components
        :param list[dict] control_objectives: List of control objectives
        :return: None
        """
        all_assets = []
        all_checklists = []
        control_implementations = []
        insert_objs = []
        update_objs = []
        implementation_objectives = []
        implementation_options = self.api.get(
            self.config["domain"] + "/api/implementationOptions"
        ).json()

        for component in existing_components:
            self.logger.info(
                "Processing Implementation Objectives for component: %s",
                component["id"],
            )
            component_assets_response = self.api.get(
                url=self.config["domain"]
                + f"/api/assets/getAllByParent/{component['id']}/components"
            )
            if component_assets_response.status_code == 204:  # No Assets, move on.
                continue
            component_assets = component_assets_response.json()
            all_assets.extend(component_assets)
            for asset in component_assets:
                # Fetch all checklists for an asset.
                all_checklists.extend(
                    self.api.get(
                        url=self.config["domain"]
                        + f"/api/securityChecklist/getAllByParent/{asset['id']}"
                    ).json()
                )
            control_implementations.extend(
                self.get_implementations(
                    parent_id=component["id"], parent_module="components"
                )
            )
        for imp in control_implementations:
            # Filter Control Objectives
            filtered_objectives = [
                obj
                for obj in control_objectives
                if obj["securityControlId"] == imp["controlID"]
            ]
            implementation_objectives.extend(
                ImplementationObjective.fetch_implementation_objectives(
                    self.app, imp["id"]
                )
            )
            new_objs, updated_objs = self.create_objectives(
                implementation=imp,
                control_objectives=filtered_objectives,
                options=implementation_options,
                all_checklists=all_checklists,
            )
            insert_objs.extend(new_objs)
            update_objs.extend(updated_objs)
        if update_objs or insert_objs:
            self.logger.info(
                "Attempting to Insert %i new implementation objectives and update %i existing implementation objectives",
                len(insert_objs),
                len(update_objs),
            )
            self.mass_update(update_objs=update_objs, insert_objs=insert_objs)
        else:
            self.logger.info("No objectives found to update or insert.")

    def update_implementation(self, existing_imp: dict, status: str) -> None:
        """
        Update implementation in RegScale via API
        :param dict existing_imp: A dict of an existing implementation
        :param str status: The implementation status
        :return: None
        """
        if existing_imp["status"] != status:
            existing_imp["status"] = status
            # Drop objectives section, not needed
            del existing_imp["objectives"]
            implementation_id = existing_imp["id"]
            response = self.api.put(
                url=self.config["domain"]
                + f"/api/controlImplementation/{implementation_id}",
                json=existing_imp,
            )
            if not response.ok:
                self.logger.error("Unable to update Implementation: %s", existing_imp)

    def parse_stig(
        self,
        file_path: Path,
        ssp_id: int,
        control_objectives: dict,
        security_controls: list[dict],
        existing_assets: list[dict] = [],
    ) -> STIG_FILE:
        """Parse Stig

        :param file_path: The file path to the STIG file
        :param ssp_id: The RegScale SSP ID
        :param control_objectives: A list of control objectives
        :param security_controls: A list of security controls
        :param existing_assets: A list of existing assets, defaults to []
        :raises requests.ConnectionError: _description_
        :raises ValueError: A generic value error
        :return: STIG_FILE
        """

        # TODO:
        # Pull down latest 800-53 rev4, drop all current objectives,
        # replace with the CCIs (make the CCIs an objective),
        # load into RegScale,
        # pull down new JSON file
        # and we will publish a DoD version

        stig_obj = None
        securityplans = []
        # check_powershell(app)
        self.logger.debug("Processing file: %s", str(file_path.absolute()))

        securityplan_response = self.api.get(
            self.config["domain"] + "/api/securityplans/getAll"
        )
        if securityplan_response.status_code == 200:
            securityplans = securityplan_response.json()
        elif securityplan_response.status_code == 401:
            raise requests.ConnectionError(
                "Unable to Authenticate to RegScale Server, \
                                                please execute `regscale login`for a fresh token."
            )

        if ssp_id not in {ssp["id"] for ssp in securityplans}:
            raise ValueError("Security plan not found on RegScale server.")
        else:
            stig_obj = STIG_FILE(
                file_path=file_path.absolute(),
                app=self.app,
                ssp_id=ssp_id,
                control_objectives=control_objectives,
                security_controls=security_controls,
                mapping=self.cci_mapping,
                assets=existing_assets,
            )
            # Search RegScale issues
            issues_url = self.config["domain"] + "/api/issues"
            regscale_existing_issues = []
            update_issues = []
            regscale_existing_issues_response = self.api.get(issues_url + "/getAll")
            if regscale_existing_issues_response.status_code == 200:
                regscale_existing_issues = regscale_existing_issues_response.json()
            new_issues = [
                asdict(iss)
                for iss in stig_obj.issue_list
                if iss.title.strip()
                not in (ex["title"].strip() for ex in regscale_existing_issues)
                and iss.status == "Open"
            ]
            if regscale_existing_issues:
                update_issues_to_process = [
                    asdict(iss)
                    for iss in stig_obj.issue_list
                    if iss.title.strip()
                    in {ex["title"].strip() for ex in regscale_existing_issues}
                    and iss.parentId
                    in {ex["parentId"] for ex in regscale_existing_issues}
                ]
                # update ids for update_issues
                for update_iss in update_issues_to_process:
                    existing = [
                        item
                        for item in regscale_existing_issues
                        if item["title"] == update_iss["title"]
                        and item["parentId"] == update_iss["parentId"]
                        and item["parentModule"] == update_iss["parentModule"]
                    ]
                    if existing:
                        existing = existing.pop()
                        # Get the key from existing record
                        update_iss["id"] = existing["id"]
                        update_iss["description"] = (
                            existing["description"]
                            if "description" in existing.keys()
                            else update_iss["description"]
                        )
                        update_iss["dueDate"] = (
                            existing["dueDate"]
                            if "dueDate" in existing.keys()
                            else update_iss["dueDate"]
                        )
                        if (
                            update_iss["status"] == "Closed"
                            and update_iss["dateCompleted"] is None
                        ):
                            update_iss["dateCompleted"] = get_current_datetime()
                        update_iss["parentId"] = existing["parentId"]
                        update_iss["parentModule"] = "securityplans"
                        if update_iss["status"] != existing["status"]:
                            update_iss["dateFirstDetected"] = existing[
                                "dateFirstDetected"
                            ]
                            update_issues.append(update_iss)
            for issue in update_issues:
                result = self.api.put(url=f"{issues_url}/{issue['id']}", json=issue)
                if not result.ok:
                    self.logger.warning("Unable to update issue: %s", issue)
            for issue in new_issues:
                result = self.api.post(url=issues_url, json=issue)
                if not result.ok:
                    self.logger.warning("Unable to insert issue: %s", issue)
        return stig_obj

    def post_options(self, options: list[dict]) -> None:
        """Post Implementation Option to RegScale
        :param list[dict] options: A list of Implementation Options
        :return: None
        """
        response = self.api.post(
            url=self.config["domain"] + "/api/implementationOptions/batchcreate",
            json=options,
        )
        if not response.raise_for_status():
            self.logger.debug(
                "Created a New Implementation Option: %s",
                (dumps(response.json(), indent=2)),
            )

    def check_components(self) -> list[dict]:
        """
        Create Hardware/Software pair of components, if necessary
        :return: A list of components
        :rtype: list[dict]
        """

        def post_component(component: Component):
            """Post a new component

            :param component: A new component
            """
            response = self.api.post(
                self.config["domain"] + "/api/components", json=asdict(component)
            )
            if not response.raise_for_status():
                self.logger.info(
                    "A new component, %s #%i, has been created!",
                    component["componentType"],
                    response.json()["id"],
                )
            component_id = response.json()["id"]
            mapping = {"componentId": component_id, "securityPlanId": self.regscale_ssp}
            self.api.post(
                url=self.config["domain"] + "/api/componentMapping", json=mapping
            )

        existing = []
        # types = set()
        for file in self.files:
            existing = Component.get_components_from_ssp(
                app=self.app, ssp_id=self.regscale_ssp
            )
            titles = {cmp["title"] for cmp in existing}
            _, _, title = self._get_metadata(file)
            component_title = f"{title} - Hardware"
            if component_title not in titles:
                component = Component(
                    title=component_title,  # TODO: STIG_NAME - Hardware
                    description="Hardware assets.",
                    componentType="hardware",
                    componentOwnerId=self.config["userId"],
                    securityPlansId=self.regscale_ssp,
                )
                if component:
                    post_component(component)
            if f"{title} - Software" not in titles:
                component_title = f"{title} - Software"
                component = Component(
                    title=component_title,  # TODO: STIG_NAME - Software
                    description="Software assets.",
                    componentType="software",
                    componentOwnerId=self.config["userId"],
                    securityPlansId=self.regscale_ssp,
                )
                if component:
                    post_component(component)

        return Component.get_components_from_ssp(app=self.app, ssp_id=self.regscale_ssp)

    def update_options(self, control_objectives: list[dict]) -> None:
        """
        Create all the Implementation Options this integration will need
        :param list[dict] control_objectives: A list of control objectives
        :return: None
        """
        opts = []

        self.logger.info("Found NIST Rev 4 DOD Catalogue..")
        # Get All CCI Objectives
        control_objectives = [obj for obj in control_objectives if "CCI" in obj["name"]]
        all_options = self.api.get(
            url=self.config["domain"] + "/api/implementationOptions"
        ).json()
        # Create two options per objective if they do not exist
        for obj in control_objectives:
            # Check to see if option exists, if not build it
            options = [
                opt
                for opt in all_options
                if opt["securityControlId"] == obj["securityControlId"]
            ]
            names = {name["name"] for name in options}
            opt = None
            if "Not Implemented Option" not in names:
                # Create Not Implemented Option
                opt = ImplementationOption(
                    id=0,
                    uuid=None,
                    createdById=self.config["userId"],
                    dateCreated=get_current_datetime(),
                    lastUpdatedById=self.config["userId"],
                    dateLastUpdated=get_current_datetime(),
                    name="Not Implemented Option",
                    description="Not Implemented",
                    archived=False,
                    securityControlId=obj["securityControlId"],
                    objectiveId=obj["id"],
                    otherId="",
                    acceptability="Not Implemented",
                )
                opts.append(asdict(opt))
            if "Fully Implemented Option" not in names:
                # Create Fully Implemented Option
                opt = ImplementationOption(
                    id=0,
                    uuid=None,
                    createdById=self.config["userId"],
                    dateCreated=get_current_datetime(),
                    lastUpdatedById=self.config["userId"],
                    dateLastUpdated=get_current_datetime(),
                    name="Fully Implemented Option",
                    description="Fully Implemented",
                    archived=False,
                    securityControlId=obj["securityControlId"],
                    objectiveId=obj["id"],
                    otherId="",
                    acceptability="Fully Implemented",
                )
                opts.append(asdict(opt))
        if opts:
            self.logger.info("Posting %i new implementation options", len(opts))
            self.post_options(options=opts)

    def get_catalog_id(
        self,
        title="NIST Special Publication 800-53 Revision 4: Security and Privacy Controls for Federal Information Systems and Organizations - DOD",
    ) -> int:
        """Return the RegScale Catalogue ID

        :param title: The catalog title to look up
        :return: A catalog id
        :rtype: int
        """
        cat_id = None
        cats = self.api.get(url=self.config["domain"] + "/api/catalogues").json()
        cat = [cat["id"] for cat in cats if cat["title"] == title]
        if cat:
            cat_id = cat[0]
        return cat_id

    def get_implementations(
        self, parent_id: int, parent_module: str = "components"
    ) -> list[dict]:
        """Return a list of control implementations by parent

        :param parent_id: _description_
        :param parent_module: _description_, defaults to "components"
        :return: A list of control implementations
        :rtype: list[dict]
        """
        control_implementations = []
        response = self.api.get(
            self.config["domain"]
            + f"/api/controlimplementation/getAllByParent/{parent_id}/{parent_module}"
        )
        if response.ok:
            control_implementations = response.json()
        return control_implementations

    def get_security_controls(self) -> Tuple[int, list[dict]]:
        """Fetch a list of security controls by catalog, return controls and catalog id.
        :return: A tuple of catalog id and a list of security controls
        :rtype: Tuple[int, list[dict]]
        """
        cat_id = self.get_catalog_id()
        security_controls = []
        try:
            response = self.api.get(
                self.config["domain"]
                + f"/api/securityControls/getAllByCatalog/{cat_id}"
            )
            if not response.raise_for_status():
                security_controls = response.json()
        except (JSONDecodeError, IndexError) as jex:
            self.logger.error(jex)
        return cat_id, security_controls

    def get_control_objective(self, security_control_id: int) -> list[dict]:
        """
        Fetch a list of control objectives by security control ID
        :param int security_control_id: Security control ID to get controls for
        :return: A list of control objectives with the associated security control ID
        :rtype: list[dict]
        """
        control_objectives = []
        try:
            response = self.api.get(
                self.config["domain"]
                + f"/api/controlObjectives/getByControl/{security_control_id}"
            )
            if not response.raise_for_status():
                control_objectives.extend(response.json())
        except (JSONDecodeError, IndexError) as jex:
            self.logger.error(jex)
        return control_objectives

    def get_control_objectives(self, existing_components: list) -> list[dict]:
        """
        Fetch a list of control objectives by existing_components
        :param list[dict] existing_components: A list of existing components
        :return: A list of control objectives
        :rtype: list[dict]
        """
        control_implementations = []
        control_objectives = []
        for component in existing_components:
            control_implementations.extend(
                self.get_implementations(
                    parent_id=component["id"], parent_module="components"
                )
            )
        for control in control_implementations:
            control_objectives.extend(self.get_control_objective(control["controlID"]))
        return control_objectives

    def pull_fresh_asset_list(self) -> list[Asset]:
        """
        Pull all assets from RegScale via API
        :return: A list of assets
        :rtype: list[Asset]
        """
        existing_assets = []
        for component in self.check_components():
            existing_asset_response = self.api.get(
                self.config["domain"]
                + f"/api/assets/getAllByParent/{component['id']}/components"
            )
            if existing_asset_response.status_code != 204:  # Empty content is 204
                existing_assets = [
                    Asset.from_dict(asset) for asset in existing_asset_response.json()
                ]

        return existing_assets

    def _get_metadata(self, file: Path) -> Tuple[dict, dict, str]:
        """
        Return metadata and title from a STIG file
        :param Path file: A file path.
        :return: Tuple of metadata (dict) and title
        :rtype: Tuple[dict, dict, str]
        """
        metadata = {}
        obj = {}
        title = ""
        with open(file, "r", encoding="utf-8"):
            obj = xml_file_to_dict(file)
            metadata = obj["CHECKLIST"]["STIGS"]["iSTIG"]["STIG_INFO"]["SI_DATA"]
            title = (
                [dat["SID_DATA"] for dat in metadata if dat["SID_NAME"] == "title"][0]
                .replace("Security Technical Implementation Guide", "")
                .strip()
            )
        return obj, metadata, title

    def build_assets(
        self, existing_components: list[dict]
    ) -> Tuple[list[dict], list[Asset]]:
        """
        Build assets one by one before processing, and avoid race conditions with database
        :param list[dict] existing_components: List of existing components
        :return: A tuple of a list of assets and a list of components
        :rtype: Tuple[list[dict], list[Asset]]
        """

        existing_assets = []
        cci_set = set()
        existing_assets = self.pull_fresh_asset_list()
        self.logger.info("Building assets...")
        for file in self.files:
            self.logger.info("Loading asset(s) from %s", file)
            obj, metadata, title = self._get_metadata(file)
            self.logger.debug("Metadata: %s", metadata)
            obj_asset = obj["CHECKLIST"]["ASSET"]
            asset_category = (
                "Hardware" if obj_asset["ASSET_TYPE"] == "Computing" else "Software"
            )
            asset_type = "Other"
            category_components = [
                component
                for component in existing_components
                if component["componentType"].lower() == asset_category.lower()
            ]
            stig_vulns = obj["CHECKLIST"]["STIGS"]["iSTIG"]["VULN"]
            for vuln in stig_vulns:
                if isinstance(vuln, dict) and isinstance(vuln["STIG_DATA"], list):
                    for rule in vuln["STIG_DATA"]:
                        if rule["VULN_ATTRIBUTE"].lower() == "cci_ref":
                            if "CCI" in rule["ATTRIBUTE_DATA"]:
                                cci_set.add(rule["ATTRIBUTE_DATA"])
                elif isinstance(vuln, str):
                    # Get cci from dict
                    try:
                        cci = [
                            dat
                            for dat in stig_vulns["STIG_DATA"]
                            if dat["VULN_ATTRIBUTE"] == "CCI_REF"
                            and "ATTRIBUTE_DATA" in dat.keys()
                            and "CCI" in dat["ATTRIBUTE_DATA"]
                        ][0]["ATTRIBUTE_DATA"]
                        cci_set.add(cci_set.add(cci))
                    except IndexError as iex:
                        self.logger.error("Unable to process asset: %s", iex)
                    except TypeError as tex:
                        self.logger.error("Unable to process asset: %s", tex)
            mac = (
                obj_asset["HOST_MAC"]
                if validate_mac_address(obj_asset["HOST_MAC"])
                else None
            )

            if obj_asset["HOST_IP"]:
                component_id = [
                    cat["id"]
                    for cat in category_components
                    if cat["title"] == f"{title} - {asset_category}"
                ].pop()
                new_asset = Asset(
                    name=title,
                    status="Active (On Network)",
                    assetOwnerId=self.app.config["userId"],
                    assetCategory=asset_category,
                    description=format_data_to_html(obj_asset),
                    ipAddress=obj_asset["HOST_IP"],
                    macAddress=mac.upper(),
                    assetType=asset_type,
                    parentId=component_id,
                    parentModule="components",
                    fqdn=obj_asset["HOST_FQDN"],
                    otherTrackingNumber=obj_asset["TARGET_KEY"],
                )
                if new_asset not in existing_assets:
                    res = Asset.insert_asset(app=self.app, obj=new_asset)
                    if res.ok:
                        # Post mapping
                        mapping = {
                            "assetId": res.json()["id"],
                            "componentId": component_id,
                        }
                        self.api.post(
                            url=self.config["domain"] + "/api/assetmapping",
                            json=mapping,
                        )

        existing_assets = self.pull_fresh_asset_list()

        return list(cci_set), existing_assets

    def process(self, regscale_ssp_id: click.INT):
        """
        Process Stig Files
        :param click.INT regscale_ssp_id: RegScale SSP ID
        :raises ValueError: A ValueError is raised if the SSP ID is invalid
        :return: None
        """

        if (
            self.api.get(
                url=self.config["domain"] + f"/api/securityplans/{regscale_ssp_id}"
            ).status_code
            == 204
        ):
            raise ValueError("Invalid SSP ID")

        existing_components = self.check_components()
        cci_list, existing_assets = self.build_assets(
            existing_components=existing_components
        )
        cat_id, security_controls = self.get_security_controls()
        control_objectives, _ = self.build_implementations(
            existing_assets=existing_assets,
            cci_list=cci_list,
            cat_id=cat_id,
        )
        # control_objectives = get_control_objectives(app, existing_components)
        for file in track(
            self.files, description=f"Processing {len(self.files)} Stig Files"
        ):
            # Code will need to be syncranous unless there are some database FK constraints
            self.parse_stig(
                file,
                regscale_ssp_id,
                control_objectives,
                security_controls,
                existing_assets,
            )
        self.logger.info("Updating Options")
        self.update_options(control_objectives)
        self.update_component_implementation_objectives(
            existing_components, control_objectives
        )
        self.update_component_implementations()
        self.update_ssp_implementation_objectives()
        self.update_ssp_issues()
        self.logger.info("Done!")
