import json
import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, APIRouter, Response, status, Query
from ldap3 import Connection, Server
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import config
from domain.switch_management import TypeSwitch
from output.cisco_prime_output import CiscoPrimeOutput
from output.contact_sheet import ContactSheet
from output.models.activity_logs_database import ActivityLogsData
from output.models.contact_database import Contacts
from output.models.equipments_database import EquipmentsData
from output.models.equipments_directories_database import EquipmentsDirectoriesData
from output.models.equipments_group_database import EquipmentsGroupData
from output.models.favorite_links_database import FavoriteLinksData
from output.models.label_database import Labels
from output.models.site_database import Sites, SitesContacts
from output.models.user_database import UserData
from output.models.building_database import BuildingData
from output.record_dns_bind9 import Bind9
from output.shell.configs_shell import ConfigsShell
from output.shell.data_backup_shell import BackupShell
from output.shell.equipment_shell import EquipmentShell
from output.shell.script_model_shell import ScriptModelShell
from output.shell.switch_shell import SwitchShell
from output.tools.grafana_shell import GrafanaShell
from output.building_ansible import BuildingAnsible
from production.config_files_data import syslog_ng, promtail_conf, promtail_service, loki_conf, loki_service, base, \
    clients, count, top_top_errors

app = FastAPI()
temp = APIRouter(prefix='/api/v1')
app.include_router(temp)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users")
# Ok
async def retrieve_data_user(data: dict):
    name: str = data["name"]
    password: str = data["password"]
    user_admin = False
    user_auth = False
    change_password = False

    if config.connexion_mode == "ldap":
        organization_name = config.ldap_organization_name
        ldap_url_base = f"dc={config.ldap_url_prefix},dc={config.ldap_url_suffix}"
        server = Server(f"ldap://{config.ldap_host}:{config.ldap_port}")

        ldap_connection = Connection(server, user=f"cn={name},ou={organization_name},{ldap_url_base}",
                                     password=password)
        if ldap_connection.bind():
            user_auth = True

    elif config.connexion_mode == "local":
        user = UserData(username=name, password=password)
        user.hash_pass()
        user = user.user_check()
        if user:
            change_password = user.change_pwd
            user_auth = True
            user_admin = user.admin

    if user_auth:
        activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=name,
                                    action="Connexion")
        activity.create_activity_log()

    return {"response": user_auth, "admin": user_admin, "change_password": change_password}


@app.post("/sessions")
# Ok : API NORM
async def user_logout(data: dict):
    activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                action="Déconnexion")
    activity.create_activity_log()


@app.post("/switches")
# Ok
async def save_all_configs():
    switch = SwitchShell()
    value = switch.versioning_configs_from_ftp()
    if value:
        response_content = {"message": "Sauvegarde des switchs terminée !"}
        response_status = 200
    else:
        response_content = {"message": "Une erreur est survenue lors de la sauvegarde des switchs"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/contacts")
# Ok
async def get_contacts():
    return ContactSheet.get_all_contact_json()


@app.get("/switches/templates")
# Ok
async def get_list_templates():
    return ScriptModelShell.get_all_templates_content(templates_directory=config.templates_directory_path)


@app.post("/switches/template")
# Ok
async def retrieve_template(data: dict):
    name: str = data["type"]
    command: list = data["command"].split("\n")
    variables: dict = {}
    for variable in data["variables"]:
        variables[variable] = ""

    ScriptModelShell.create_provisioning_templates(name, command, variables)


@app.post("/templates/equipments")
# Ok
async def execution_template_equipments(data: dict):
    equipments_group: dict = data["equipments_group"]
    equipments_group_selected: list = data["selected_equipments_group"]
    file_for_commands: str = data["template_name"]
    data_template: dict = data["values_templates_selected"]
    script_exec = ScriptModelShell()
    list_eq = []
    value = False
    try:
        for equipment_gr in equipments_group:
            if equipment_gr in equipments_group_selected:
                for eq in equipments_group[equipment_gr]:
                    equipment = EquipmentShell(name=eq['name'], ip=eq['ip'])
                    list_eq.append(equipment)
        if list_eq:
            script_exec.modify_template_before_execution(file_name=file_for_commands,
                                                         command_template=data_template['commands'],
                                                         variables_template=data_template['variables'])
            value = script_exec.exec_commands_on_equipments(file_name=file_for_commands, list_equipments=list_eq)

        if value:
            response_content = {"message": "Execution terminée !"}
            response_status = 200
        else:
            response_content = {"message": "Une erreur est survenu lors de l'exécution"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de l'exécution {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


# sudo lsof -t -i tcp:8000 | xargs kill -9 : to stop the server
@app.post("/templates")
# Ok
async def remove_template(template_name: str):
    switch = SwitchShell(switch_type=TypeSwitch(name=template_name.split("_")[0]))

    date: str = f"{template_name.split('_')[1]}_{template_name.split('_')[2]}"

    return Response(status_code=status.HTTP_200_OK) if ScriptModelShell.remove_template(switch.switch_type.name,
                                                                                        date=date) == 0 else Response(
        status_code=status.HTTP_404_NOT_FOUND)


@app.post("/templates/edition")
# Ok
async def edit_template(data: dict):
    name: str = data["templateName"]
    command: list = data["cmd"]
    variables: dict = data["vars"]
    new_variables = {variable: "" for variable in data["newVars"]}
    variables.update(new_variables)

    ScriptModelShell.modify_template_before_execution(file_name=name,
                                                      command_template=command,
                                                      variables_template=variables)


@app.get("/equipments/groups/primes")
async def get_cisco_prime_equipments():
    return CiscoPrimeOutput.get_all_devices()


@app.get("/equipments/groups")
# Ok
async def get_equipments_and_groups():
    # V1.0 : Inventory
    # inventory_path = config.inventory_local_directory
    # inventory_name = config.inventory_file_name
    # return EquipmentShell.load_all(f"{inventory_path}/{inventory_name}")
    # V2.0 : Database
    return EquipmentsGroupData.get_all()


@app.post("/equipments/groups")
# Ok
async def create_equipments_group(data: dict):
    value = False
    try:
        new_equipment_group = data["new_equipment"]
        values: str = data["values"]
        list_equipment_group_values = values.split('\n')

        if new_equipment_group != '':
            # V1.0 : Inventory
            # new_group_of_equipments = EquipmentShell()
            # value = new_group_of_equipments.create(name_group=new_equipment_group,
            #                                        list_values=list_equipment_group_values)
            # V2.0 : Database
            new_group_of_equipments = EquipmentsGroupData()
            value = new_group_of_equipments.new_group_and_equipments(new_name_group=new_equipment_group,
                                                                     list_equipments=list_equipment_group_values)
        if value:
            response_content = {"message": f"Le groupe d'équipement {new_equipment_group} a bien été créé"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la création du groupe d'équipement {new_equipment_group}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la modification du groupe d'équipement {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.put("/equipments/groups")
# Ok
async def edit_equipments_and_group(data: dict):
    value = False
    try:
        equipment_group_selected = data["equipment_selected"]
        values: str = data["values"]
        id_group_selected = data["id_group_selected"]
        list_equipment_group_values = values.split('\n')

        if equipment_group_selected != '':
            # V1.0 : Inventory
            # edit_group_of_equipments = EquipmentShell()
            # value = edit_group_of_equipments.edit(name_group=equipment_group_selected,
            #                                       list_values=list_equipment_group_values)
            # V2.0 : Database
            new_group_of_equipments = EquipmentsGroupData.get_group_equipment_by_id(id_group_selected)
            value = EquipmentsGroupData.update_group_and_equipments(my_group=new_group_of_equipments,
                                                                    name_group=equipment_group_selected,
                                                                    list_values=list_equipment_group_values)
        if value:
            response_content = {"message": f"Le groupe d'équipement {equipment_group_selected} a bien été modifié"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la modification du groupe d'équipements {equipment_group_selected}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la modification du groupe d'équipements {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.delete("/equipments/groups")
# Ok
async def remove_equipments_group(data: dict):
    value = False
    try:
        equipment_group_to_remove = data["group_selected"]

        if equipment_group_to_remove != '':
            # V1.0 : Inventory
            # remove_group_of_equipments = EquipmentShell()
            # value = remove_group_of_equipments.remove(name_group=equipment_group_to_remove)
            # V2.0 : Database
            id_group_selected = data["id_group_selected"]
            my_group = EquipmentsGroupData.get_group_equipment_by_id(id_group_selected)
            value = my_group.delete()
        if value:
            response_content = {
                "message": f"Suppression du groupe d'équipement {equipment_group_to_remove} avec succès"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la suppression du groupe d'équipement {equipment_group_to_remove}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la suppression du groupe d'équipement {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/equipments")
async def get_equipments():
    return EquipmentsData.get_all()


@app.post("/equipments")
# Ok
async def create_equipment(data: dict):
    value = False
    try:
        id_group = data["id_group_selected"]
        values: str = data["values"]
        name_equipment = values.split(' ')[0]

        if id_group is not None:
            new_equipment = EquipmentsData(name=name_equipment, ip=values.split(' ')[1])
            new_equipment.group = EquipmentsGroupData.get_group_equipment_by_id(id_group)
            value = new_equipment.create()

        if value:
            response_content = {"message": f"L'équipement {name_equipment} a bien été créé"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la création du nouvel équipement {name_equipment}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la suppression du nouvel équipement {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.put("/equipments")
# Ok
async def update_equipment(data: dict):
    value = False
    try:
        id_equipment = data["id_equipment_selected"]
        name_group = data["name_group_selected"]
        values: str = data["values"]
        name_equipment = values.split(' ')[0]

        if id_equipment is not None:
            my_equipment = EquipmentsData.get_equipment_by_id(id_equipment)
            if my_equipment is not None:
                my_equipment.name = name_equipment
                my_equipment.ip = values.split(' ')[1]
                value = my_equipment.update()

        if value:
            response_content = {"message": f"L'équipement {name_equipment} dans {name_group} a bien été modifié"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la modification de l'équipement {name_equipment}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la modification de l'équipement {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.delete("/equipments")
# Ok
async def delete_equipment(data: dict):
    value = False
    try:
        id_equipment = data["id_equipment_selected"]
        name_equipment = data["name_equipment_selected"]
        name_group = data["name_group_selected"]

        if id_equipment is not None:
            my_equipment = EquipmentsData.get_equipment_by_id(id_equipment)
            value = my_equipment.delete()

        if value:
            response_content = {"message": f"L'équipement {name_equipment} dans {name_group} a bien été supprimé"}
            response_status = 200
        else:
            response_content = {
                "message": f"Une erreur est survenu lors de la suppression de l'équipement {name_equipment} dans {name_group}"}
            response_status = 500

    except Exception as err:
        response_content = {"message": f"Une erreur est survenu lors de la suppression de l'équipement {err}"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/annuaire")
# Ok
async def get_list_sites_contacts_labels():
    return {"Contacts": Contacts.get_all(), "Sites": Sites.get_all(), "Labels": Labels.get_all()}


@app.post("/annuaires/contacts")
# Ok : API NORM
async def create_contact(data: dict):
    contact = Contacts()

    contact.first_name = data["firstName"]
    contact.last_name = data["lastName"]
    contact.number = data["phone"]
    contact.mail = data["email"]
    contact.address = data["address"]
    contact.commentary = data["comment"]

    contact.create()


@app.put("/annuaires/contacts")
# Ok : API NORM
async def edit_contact(data: dict):
    contact = Contacts()

    contact.id = data["id"]
    contact.first_name = data["firstName"]
    contact.last_name = data["lastName"]
    contact.mail = data["mail"]
    contact.address = data["address"]
    contact.number = data["phone"]
    contact.commentary = data["comment"]

    contact.update()


@app.delete("/annuaires/contacts")
# Ok : API NORM
async def supp_contact(data: dict):
    contact = Contacts()

    contact.id = data["id"]

    contact.delete()


@app.post("/annuaires/sites")
# Ok : API NORM
async def create_sites(data: dict):
    site = Sites()

    if data["siteName"]:
        site.site_name = data["siteName"]
        site.create()


@app.delete("/annuaires/sites")
# Ok : API NORM
async def supp_site(data: dict):
    site = Sites()

    site.id = data["id"]

    site.delete()


@app.put("/annuaires/sites")
# Ok : API NORM
async def edit_site(data: dict):
    site = Sites()

    site.id = data["id"]
    site.site_name = data["siteName"]

    site.update()


@app.post("/annuaires/sites/contacts")
# Ok : API NORM
async def add_contact_in_site(data: dict):
    site = Sites(id=data["siteId"])
    previous_contacts = [ids for ids in site.get_contacts_by_site_id().keys()]
    new_contacts = [ids.get("id") for ids in data["contactsList"]]
    contacts_to_add = [contact for contact in new_contacts if contact not in previous_contacts]
    contacts_to_remove = [contact for contact in previous_contacts if contact not in new_contacts]

    for contact_id in contacts_to_add:
        site_contact = SitesContacts(site_id=site.id)
        site_contact.contact_id = contact_id
        site_contact.link_contacts_sites()

    for contact_id in contacts_to_remove:
        SitesContacts.remove_link_between_contacts_sites(id_site=site.id, id_contact=contact_id)


@app.post("/annuaires/contacts/sites")
# Ok : API NORM
async def add_site_in_contact(data: dict):
    contact = Contacts(id=data["contactId"])

    sites = [int(ids) for ids in data["sites"]]
    previous_sites = [ids for ids in contact.get_sites_by_contact_id().keys()]
    sites_to_add = [ids for ids in sites if ids not in previous_sites]
    sites_to_remove = [ids for ids in previous_sites if ids not in sites]

    if sites_to_add:
        for site_id in sites_to_add:
            site_contact = SitesContacts(site_id=site_id, contact_id=contact.id)
            site_contact.link_contacts_sites()

    if sites_to_remove:
        for site_id in sites_to_remove:
            SitesContacts.remove_link_between_contacts_sites(id_site=site_id, id_contact=contact.id)


@app.get("/alias")
# Ok : API NORM
def check_alias(alias_name: str = Query(...)):
    # TODO récuperation liste des alias
    alias = Bind9()
    alias.open_data = ["alias", "switch", "montre", "sel", "souris"]
    alias.name = alias_name

    return alias.alias_is_available()


@app.get("/alias/hosts")
# Ok : API NORM
async def check_host(host_name: str = Query(...)):
    equipment = EquipmentShell()
    equipment.name = host_name

    return equipment.server_exists()


@app.post("/alias")
# Ok : API NORM
async def create_alias(data: dict):
    alias = Bind9()
    alias.name = data["alias_name"]
    alias.host = data["host_name"]
    # alias.create_alias()
    value = True  # depends on method create_alias()

    if value:
        activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                    action=f"Création de l'alias {alias.name} vers {alias.host}")
        activity.create_activity_log()
        response_content = {"message": "L'alias a été créé avec succès !"}
        response_status = 200
    else:
        response_content = {"message": "Une erreur est survenue lors de la création de l'alias"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/activities")
# Ok : API NORM
async def get_activities():
    return ActivityLogsData.get_all_activity_logs()


@app.get("/favorites")
# Ok : API NORM
async def get_favorites():
    return FavoriteLinksData.get_all_links()


@app.post("/favorites")
# Ok : API NORM
async def create_favorites(data: dict):
    name = data["name"]
    url = data["url"]

    favorite = FavoriteLinksData(name=name, url=url)
    favorite.add_favorite_link()

    activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                action=f"Ajout du favori {name} | Lien: {url}")
    activity.create_activity_log()


@app.delete("/favorites")
# Ok : API NORM
async def delete_favorites(data: dict):
    favorite = FavoriteLinksData().get_favorite_link_by_id(data["id"])

    activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                action=f"Suppression du favori {favorite.name} | Lien: {favorite.url}")
    activity.create_activity_log()

    favorite.delete_favorite_link()


@app.put("/favorites")
# Ok : API NORM
async def update_favorites(data: dict):
    favorite = FavoriteLinksData(id=data["id"], name=data["name"], url=data["url"])
    favorite.edit_favorite_link()

    activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                action=f"Modification du favori {favorite.name} | Lien: {favorite.url}")
    activity.create_activity_log()


@app.get("/buildings")
# Ok : API NORM
async def get_wifis_buildings():
    return BuildingData.get_all()


@app.post("/buildings/commands")
# Ok : API NORM
async def enable_building_wifi(data: dict):
    wifi = BuildingAnsible()
    wifi.name = data["building"]
    # wifi.execute("script_ansible")

    activity = ActivityLogsData(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), author=data["user"],
                                action=f"Activiation du wifi dans le batiment {wifi.name}")
    activity.create_activity_log()


@app.post("/buildings")
# Ok : API NORM
async def create_building(data: dict):
    name = data["name"]
    building_to_create = BuildingData(name=name)

    try:
        building_to_create.create()
        logging.info(f"{name} a été créé avec succès !")
        response_content = {f"message": f"{name} créé avec succès !"}
        response_status = 200
    except Exception as e:
        logging.error(f"Erreur lors de la création du bâtiment {name} : {e}")
        response_content = {"message": "Un problème est survenu lors de la création du bâtiment"}
        response_status = 500
    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.delete("/buildings")
# Ok : API NORM
async def delete_building(data: dict):
    try:
        building_to_delete = BuildingData().get_by_id(data["buildingId"])
        name = building_to_delete.name
        building_to_delete.delete()
        logging.info(f"{name} a été supprimé avec succès !")
        response_content = {f"message": f"{name} a été supprimé avec succès !"}
        response_status = 200
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du bâtiment : {e}")
        response_content = {"message": "Un problème est survenu lors de la suppression du bâtiment"}
        response_status = 500
    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.put("/buildings")
# Ok : API NORM
async def update_building(data: dict):
    new_name = data["name"]
    try:
        building_to_update = BuildingData().get_by_id(data["buildingId"])
        building_to_update.name = new_name
        building_to_update.update()
        logging.info(f"{new_name} a été modifié avec succès !")
        response_content = {f"message": f"{new_name} a été modifié avec succès !"}
        response_status = 200
    except Exception as e:
        logging.error(f"Erreur lors de la modification du bâtiment : {e}")
        response_content = {"message": "Un problème est survenu lors de la modification du bâtiment"}
        response_status = 500
    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.put("/buildings/equipments")
# Ok : API NORM
async def link_unlink_equipments_to_building(data: dict):
    building = BuildingData().get_by_id(b_id=data["buildingId"])
    previous_equipments = [equipment.id for equipment in building.equipments]
    new_equipments = [equipment for equipment in data["equipmentsIds"]]
    equipments_to_add = [equipment for equipment in new_equipments if equipment not in previous_equipments]
    equipments_to_remove = [equipment for equipment in previous_equipments if equipment not in new_equipments]

    try:
        for equipment_id in equipments_to_add:
            equipment = EquipmentsData().get_equipment_by_id(id_equipment=equipment_id)
            building.link_equipment(equipment=equipment)

        for equipment_id in equipments_to_remove:
            equipment = EquipmentsData().get_equipment_by_id(id_equipment=equipment_id)
            building.unlink_equipment(equipment=equipment)

        logging.info(f"Les équipements du bâtiment {building.name} ont été mis à jour avec succès !")
        response_content = {"message": f"Les équipements du bâtiment {building.name} ont été mis à jour avec succès !"}
        response_status = 200

    except Exception as e:
        logging.error(f"Erreur lors de la modification des équipements du bâtiment {building.name} : {e}")
        response_content = {
            "message": f"Un problème est survenu lors de la modification des équipements du bâtiment {building.name}"}
        response_status = 500
    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/equipments/versions")
# Ok : API NORM
async def get_equipments_diff_versions():
    return EquipmentShell.version_alert(
        actual_version=f"{config.inventory_local_directory}/{config.inventory_file_name}",
        new_version=f"{config.inventory_local_directory}/{config.inventory_file_version}")


@app.post("/tools")
# Ok : API NORM
async def edit_local_param(data: dict):
    if not hasattr(edit_local_param, "configuration"):
        edit_local_param.configuration = ConfigsShell()
        edit_local_param.configuration.config_file_path = config.config_file

    sudo = data["useSudo"]
    tool = data["tool"]
    operation = data["operation"]
    input_values = data["inputValues"]

    tools_dict = {
        "connection": ["grafana_host", "grafana_port", "grafana_username"],
        "grafana": ["grafana_wget_url", "grafana_ini_file"],
        "loki": ["loki_wget_url", "loki_yaml_file", "loki_service_file"],
        "promtail": ["promtail_wget_url", "promtail_yaml_file", "promtail_service_file"]
    }

    tool_keys = tools_dict.get(tool, [])

    cleaned_input_values = {k: v for k, v in input_values.items() if k in tool_keys}
    cleaned_input_values["use_sudo"] = sudo

    tools = {
        "grafana": {"method": GrafanaShell().install_grafana, "success_message": "Grafana installé avec succès"},
        "loki": {"method": GrafanaShell().install_loki, "success_message": "Loki installé avec succès"},
        "promtail": {"method": GrafanaShell().install_promtail, "success_message": "Promtail installé avec succès"},
    }

    if operation == "install":
        if tool in tools:
            try:
                # TODO : Activate next line to install tools
                # tools[tool]["method"]()
                response_content = {"message": tools[tool]["success_message"]}
                response_status = 200
            except Exception as e:
                response_content = {"message": f"Erreur lors de l'installation de {tool}: {e}"}
                response_status = 500
        else:
            response_content = {"message": "Outil inconnu"}
            response_status = 500
    elif operation == "save":
        try:
            for key, value in cleaned_input_values.items():
                edit_local_param.configuration.variable_name = key
                edit_local_param.configuration.variable_value = value
                # TODO : Activate next line to save configuration
                # edit_local_param.configuration.edit_variable()
            response_content = {"message": "Configuration sauvegardée"}
            response_status = 200
        except Exception as e:
            response_content = {"message": f"Erreur lors de la sauvegarde: {e}"}
            response_status = 500
    else:
        response_content = {"message": "Opération inconnue"}
        response_status = 500

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/tools")
# ok : API NORM
async def get_tools():
    return {
        "host": config.grafana_host,
        "port": config.grafana_port,
        "user": config.grafana_username,
        "grafanaUrl": config.grafana_wget_url,
        "grafanaIni": config.grafana_ini_file,
        "lokiUrl": config.loki_wget_url,
        "lokiYaml": config.loki_yaml_file,
        "lokiService": config.loki_service_file,
        "promtailUrl": config.promtail_wget_url,
        "promtailYaml": config.promtail_yaml_file,
        "promtailService": config.promtail_service_file,
        "syslog": syslog_ng,
        "base": base,
        "clients": clients,
        "count": count,
        "top": top_top_errors,
        "loki-yaml-content": loki_conf,
        "loki-service-content": loki_service,
        "promtail-yaml-content": promtail_conf,
        "promtail-service-content": promtail_service,
    }


@app.get("/settings")
async def get_settings():
    load_dotenv()
    return {
        "connexionMode": config.connexion_mode,
        "ldapHost": config.ldap_host,
        "ldapPort": config.ldap_port,
        "ldapPrefix": config.ldap_url_prefix,
        "ldapSuffix": config.ldap_url_suffix,
        "ldapOrganizationName": config.ldap_organization_name,

        "appName": config.application_name,  # os.getenv("APPLICATION_NAME"),
        "frontHost": config.frontend_host,
        "nvmURL": config.nvm_wget_url,

        "ansibleUsername": config.ansible_username,
        "ansiblePort": config.ansible_port,
        "ansibleHost": config.ansible_host,

        "ftpHost": config.ftp_host,
        "ftpUsername": config.ftp_username,
        "ftpDir": config.equipement_ftp_remote_directory,
        "ftpPwd": ConfigsShell.get_value('ftp_password'),

        "switchLocalDir": config.switch_configs_local_directory,
        "switchRemoteGit": config.repository_to_save_configs_for_all_switches_with_ssh,
        "savingHour": config.saving_hour,

        "inventoryDir": config.inventory_local_directory,
        "inventoryFileName": config.inventory_file_name,
        "inventoryVersion": config.inventory_file_version,
        "inventorySeparator": config.separateur,
        "EquipmentsPort": config.equipments_port,
        "EquipmentsPwd": ConfigsShell.get_value('equipments_password'),

        "DNSType": config.DNS_type,
        "aliasFile": config.alias_file,
        "configPath": f"{config.root_dir}/config.py",

        "logs_path": config.logs_file_path,
        "logs_level": config.debug_level,
        "database_resource": config.database_resource,
        "database_file": config.database_file,
        "excel_file": config.excel_file_path,
        "template_dir": config.templates_directory_path,

        "envPath": config.env_path,

        "backupUsername": config.backup_username,
        "backupPort": config.backup_port,
        "backupHost": config.backup_host,
        "backupTargetDir": config.backup_target_dir,
        "backupHour": config.backup_hour
    }


@app.post("/settings/local")
async def change_user_data():
    edit_local_param.configuration = ConfigsShell()
    edit_local_param.configuration.config_file_path = f"{config.root_dir}/config.py"
    try:
        edit_local_param.configuration.variable_name = "connexion_mode"
        edit_local_param.configuration.variable_value = "local"
        edit_local_param.configuration.edit_variable()
        return True
    except Exception as e:
        return None


@app.post("/settings/ldap")
async def change_ldap_param(data: dict):
    edit_local_param.configuration = ConfigsShell()
    edit_local_param.configuration.config_file_path = f"{config.root_dir}/config.py"
    if data['ldapPort'] is None:
        data['ldapPort'] = ""
    ldap_dict = {
        "ldap_host": data['ldapHost'],
        "ldap_url_prefix": data['ldapPrefix'],
        "ldap_url_suffix": data['ldapSuffix'],
        "ldap_port": data['ldapPort'],
        "ldap_organization_name": data['ldapOrgName'],
        "connexion_mode": "ldap",
    }
    # print(ldap_dict.items())
    # print(len(ldap_dict))
    for key, value in ldap_dict.items():
        edit_local_param.configuration.variable_name = key
        edit_local_param.configuration.variable_value = value
        # print(f"{key} = {value}")
        edit_local_param.configuration.edit_variable()

    return True


@app.get("/settings/users")
async def get_settings():
    return UserData.get_all()


@app.post("/settings/users")
async def add_user(data: dict):
    if data['username'] != "" and data['new_pwd'] != "":
        user = UserData(username=data['username'], password=data['new_pwd'])
        # print(user)
        if not user.get_user_by_id(data['username']):
            if data['admin']:
                user.admin = data['admin']
            if data['change_pwd_next']:
                user.change_pwd = data['change_pwd_next']
            user.create()
            return True
    return None


@app.put("/settings/users")
async def modify_user(data: dict):
    response_content = {"message": "Un problème est survenu lors de la modification de l'utilisateur"}
    response_status = 500

    if data.get("personalEdit"):
        user = UserData(username=data.get("username"), password=data.get("oldPassword"))
        user.hash_pass()
        user = user.user_check()
        if user:
            user.password = data.get("newPassword")
            user.hash_pass()
            user.change_pwd = False
            user.update()
            response_content = {"message": "Mot de passe modifié avec succès"}
            response_status = 200
        else:
            response_content = {"message": "Mot de passe actuel incorrect"}
            response_status = 500

    else:
        if data['username'] != '':
            user = UserData.get_user_by_id(data['idUser'])
            # print(user)
            user.username = data['username']
            user.admin = bool(data['admin'])
            user.change_pwd = bool(data['change_pwd_next'])
            # print(user)
            # print(f"'{data['newPassword']}'")
            if data['newPassword'] is not None and data['newPassword'] != '':
                user.password = data['newPassword']
                user.hash_pass()
                # print(user)

            user.update()
            response_content = {"message": "Utilisateur modifié avec succès"}
            response_status = 200

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.delete("/settings/users")
async def delete_user(data: dict):
    user = UserData.get_user_by_id(data['idUser'])
    if user:
        user.delete()
        return True
    return None


@app.post("/settings/front")
async def front_param(data: dict):
    front_dict = {
        "application_name": data['application_name'],
        "frontend_host": data['front_host'],
        "nvm_wget_url": data['nvm_url']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(front_dict)

    return value


@app.post("/settings/ftp")
async def ftp_param(data: dict):
    ftp_dict = {
        "ftp_host": data['ftp_host'],
        "ftp_username": data['ftp_username'],
        "equipement_ftp_remote_directory": data['ftp_dir']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(ftp_dict)
    if value:
        configuration.update_salt('ftp_password', data['ftp_password'])
    return value


@app.post("/settings/switchs")
async def switches_settings_param(data: dict):
    switchs_dict = {
        "switch_configs_local_directory": data['switch_local_dir'],
        "repository_to_save_configs_for_all_switches_with_ssh": data['switch_remote_git'],
        "saving_hour": data['saving_hour']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(switchs_dict)

    return value


@app.post("/settings/ansible")
async def ansible_settings_param(data: dict):
    if data['ansible_port'] is None:
        data['ansible_port'] = ""
    ansible_dict = {
        "ansible_host": data['ansible_host'],
        "ansible_port": data['ansible_port'],
        "ansible_username": data['ansible_username']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(ansible_dict)

    return value


@app.post("/settings/equipments")
async def equipments_param(data: dict):
    if data['equipments_port'] is None:
        return False
    equipments_dict = {
        "inventory_local_directory": data['inventory_local_directory'],
        "inventory_file_name": data['inventory_file_name'],
        "inventory_file_version": data['inventory_file_version'],
        "equipments_port": data['equipments_port'],
        "separateur": data['separateur']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(equipments_dict)
    if value:
        configuration.update_salt('equipments_password', data['equipments_password'])
    return value


@app.post("/settings/alias")
async def alias_settings_param(data: dict):
    alias_dict = {
        "DNS_type": data['DNS_type'],
        "alias_file": data['alias_file'],
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(alias_dict)

    return value


@app.post("/settings/environments")
async def alias_settings_param(data: dict):
    alias_dict = {
        "env_path": data['env_path']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(alias_dict)

    return value


@app.post("/settings/logs")
async def logs_settings_param(data: dict):
    if data['debug_level'] is None:
        return False
    logs_dict = {
        "debug_level": data['debug_level'],
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(logs_dict)

    return value


@app.post("/settings/others")
async def others_settings_param(data: dict):
    db_dict = {
        "templates_directory_path": data['templates_directory_path'],
        "excel_file_path": data['excel_file_path'],
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(db_dict)

    return value


@app.post("/settings/backup")
async def backup_param(data: dict):
    if data['backup_port'] is None:
        data['backup_port'] = ""
    backup_dict = {
        "backup_hour": data['backup_hour'],
        "backup_target_dir": data['backup_target_dir'],
        "backup_username": data['backup_username'],
        "backup_port": data['backup_port'],
        "backup_host": data['backup_host']
    }
    configuration = ConfigsShell()
    value = configuration.modify_from_dict(backup_dict)
    return value


@app.get("/equipments/directories")
# Ok : API NORM
async def get_equipments_directories():
    return EquipmentsDirectoriesData.get_all()


@app.post("/settings/monitoring")
async def add_equipment_sub_directories(data: dict):
    if data['name'] is not None:
        equipment_dir = EquipmentsDirectoriesData(name=data['name'])
        if data['frequency'] != ['', None]:
            equipment_dir.frequency = data['frequency']
        equipment_dir.create()
        return True
    return None


@app.put("/settings/monitoring")
async def modify_equipment_sub_directories(data: dict):
    equipment_dir = EquipmentsDirectoriesData.get_equipment_by_id(data['idEq'])
    if equipment_dir:
        if data['nameEq'] != '' and data['frequencyEq'] is not None:
            equipment_dir.name = data['nameEq']
            equipment_dir.frequency = data['frequencyEq']
            equipment_dir.update()
            return True
    return None


@app.delete("/settings/monitoring")
async def delete_equipment_sub_directories(data: dict):
    equipment_dir = EquipmentsDirectoriesData.get_equipment_by_id(data['idEq'])
    if equipment_dir:
        equipment_dir.delete()
        return True
    return None


@app.get("/equipments/directories/files")
async def get_equipments_directories_files():
    return EquipmentShell.get_equipments_directories_files_date_and_size()


@app.get("/versions")
async def get_package_version():
    return ConfigsShell.get_version_package()


@app.post("/settings/backup/execute")
async def add_equipment_sub_directories(data: dict):
    if data['backup_port'] is None:
        data['backup_port'] = ""
    backup_dict = {
        "backup_hour": data['backup_hour'],
        "backup_target_dir": data['backup_target_dir'],
        "backup_username": data['backup_username'],
        "backup_port": data['backup_port'],
        "backup_host": data['backup_host']
    }
    configuration = ConfigsShell()
    configuration.modify_from_dict(backup_dict)
    if BackupShell.check_ssh_connection(username=data['backup_username'], host=data['backup_host'],
                                        port=data['backup_port']):
        BackupShell.backup()
        return True
    return False


@app.post("/settings/backups/connections")
# API NORM
async def verify_backup_server_connection(data: dict):
    host = data['host']
    port = data.get('port')
    username = data['username']

    response_content = {"message": "Un problème est survenu lors de la connexion au serveur de backup"}
    response_status = 500

    if BackupShell.check_ssh_connection(username=username, host=host, port=port):
        response_content = {
            "message": "Connexion au serveur de backup réussie"
        }
        response_status = 200

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.post("/settings/equipments/connections")
# API NORM
async def verify_equipment_server_connection(data: dict):
    host = data['host']
    username = data['username']
    group = data['equipment_group']
    port = config.equipments_port

    if data['port'] is not None:
        port = data['port']

    response_content = {
        "message": f"Un problème est survenu lors de la connexion à {username} ({host}:{port}) dans {group}"}
    response_status = 500

    if EquipmentShell.check_ssh_connection(username=username, host=host, port=port, equipment_group=group):
        response_content = {
            "message": f"Connexion à {username} ({host}:{port}) dans {group} réussie"
        }
        response_status = 200

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.post("/settings/ftps/connections")
# API NORM
async def verify_ftp_server_connection(data: dict):
    host = data['host']
    username = data['username']
    pwd = data['pwd']

    response_content = {"message": "Un problème est survenu lors de la connexion au serveur FTP"}
    response_status = 500

    if EquipmentShell.check_ftp_connection(username=username, host=host, password=pwd):
        response_content = {
            "message": "Connexion au serveur FTP réussie"
        }
        response_status = 200

    return Response(status_code=response_status, content=json.dumps(response_content), media_type="application/json")


@app.get("/switchs/ports")
# API NORM
async def get_switches_ports():
    data = {
        "switch 1": [33633],
        "switch 2": [18790],
        "switch 3": [56734],
        "switch 4": [9629, 20054],
        "switch 5": [27512],
        "switch 6": [51796],
        "switch 7": [20534, 51778],
        "switch 8": [17851, 40008],
        "switch 9": [9929, 20013, 32343],
        "switch 10": [53045],
        "switch 11": [43939],
        "switch 12": [18391],
        "switch 13": [36294, 3221, 50060],
        "switch 14": [38323],
        "switch 15": [23763],
        "switch 16": [22811, 49278],
        "switch 17": [39553, 34806],
        "switch 18": [28403],
        "switch 19": [34750, 54928],
        "switch 20": [50653],
        "switch 21": [14154, 37329],
        "switch 22": [35260, 41290, 14642],
        "switch 23": [5135],
        "switch 24": [32929],
        "switch 25": [428, 36239],
        "switch 26": [7217],
        "switch 27": [60997],
        "switch 28": [55211, 3917],
        "switch 29": [35345],
        "switch 30": [61070, 401],
        "switch 31": [37594],
        "switch 32": [14677, 23381],
        "switch 33": [35137],
        "switch 34": [63360, 50807],
        "switch 35": [60913, 30254],
        "switch 36": [25022],
        "switch 37": [49270, 5860],
        "switch 38": [19590, 23711],
        "switch 39": [20054],
        "switch 40": [20013]
    }

    return data


if __name__ == "__main__":
    uvicorn.run("api.server:app", port=8000, reload=True, reload_includes=config.root_dir)
