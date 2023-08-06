from sqlalchemy import text

from output.database.database_base import engine

if __name__ == '__main__':
    rename_table_query = text("ALTER TABLE Wifi RENAME TO Building;")
    engine.execute(rename_table_query)

    rename_bld_column_query = text("ALTER TABLE Building RENAME COLUMN building TO name;")
    engine.execute(rename_bld_column_query)

    rename_eq_column_query = text("ALTER TABLE Equipments RENAME COLUMN wifi_id TO building_id;")
    engine.execute(rename_eq_column_query)
