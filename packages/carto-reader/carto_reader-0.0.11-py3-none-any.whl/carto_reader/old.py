import sys
import os.path
import csv
import pyodbc


# 1) Connexion to MSSQL Server: specify the absolute path to the driver library.
# Example of driver file path:
# "Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.7.so.2.1};"
driver = "Driver={/usr/local/lib/libmsodbcsql.17.dylib};"

# 2) Input the correct uid and password
# Example:
# "Uid=Billy;"
# "Pwd=someRobustPassword;"
uid = "Uid=;"
password = "Pwd=;"

# 3) Feel free to add or remove tables
tables_to_convert = ["MAPS_TABLE", "SETUP_TABLE", "STUDIES_TABLE", "TAG_SETUP_TABLE",
                     "PROCEDURES_TABLE", "POINTS_TABLE", "COLORS_TABLE"]


# get database path and print help if necessary
def get_database_path(argv):
    if len(argv) != 2:
        print(f'Usage: {argv[0]} /absolute/path/to/database.mdf')
        quit()
    else:
        database = argv[1]
        if database.endswith(".mdf") and database.startswith('/'):
            return database
        else:
            print(f'Invalid database path or type: must pass an absolute path to a mssql server database')
            quit()


def convert_table(cursor, table_name, output_path):
    output_file_name = output_path + "/" + table_name.lower() + ".csv"
    query = """SELECT * FROM """ + table_name
    cursor.execute(query)
    column_names = [column[0] for column in cursor.description]

    os.makedirs(os.path.dirname(output_file_name), exist_ok=True)
    # Go through the results row-by-row and write the output to a CSV file.
    # Use QUOTE_NONE, could be changed to QUOTE_NONNUMERIC or
    # QUOTE_ALL (to avoid escape character problems)
    # Use '|' as delimiter, this seems to work fine for now. Will be problematic
    # if some fields contain '|' as a character.
    with open(output_file_name, "w") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONE, delimiter='|')
        # write the column names first
        writer.writerow(column_names)
        # write the data
        for row in cursor:
            writer.writerow(row)


def convert_database(input, output_path):
    server = "Server=tcp:localhost;"
    database_name = "Database=TemporaryCartoDatabase;"
    attach_db_filename = "AttachDbFileName=" + input + ";"

    connection_string = driver + server + database_name + attach_db_filename + uid + password
    connexion = pyodbc.connect(connection_string)
    connexion.autocommit = False

    cursor = connexion.cursor()

    for table_name in tables_to_convert:
        convert_table(cursor, table_name, output_path)

    # Close the cursor and the database connection
    cursor.close()
    connexion.close()


if __name__ == '__main__':
    database_path = get_database_path(sys.argv)
    output_path = os.path.dirname(database_path) + "/converted_database"

    convert_database(database_path, output_path)


# All available tables found in the database (tested only on 1 database, there may be more):
#
# A_TAGS_TABLE
# ARCHIVE_LOG_TABLE
# AUTO_MAP_PRESETS_TABLE
# BCS_TABLE
# CARTOFINDER_SITES_TABLE
# CATHETERS_ID_TABLE
# CFAE_SETUP_TABLE
# COLOR_SCALE_SETUP_TABLE
# COLORS_TABLE
# CONFIG_ACQUIRE_TABLE
# CONFIG_CARTOFINDER_PREFERENCE_TABLE
# CONFIG_CHANNEL_TABLE
# CONFIG_CONNECTOR_TABLE
# CONFIG_CONTACT_FORCE_GUI_TABLE
# CONFIG_CONTACT_FORCE_PREFERENCE_TABLE
# CONFIG_EP_RECORDING_TABLE
# CONFIG_FILTER_TABLE
# CONFIG_HELIOS_PRESET_TABLE
# CONFIG_HUD_TOOLBAR_TABLE
# CONFIG_LAYOUT_TABLE
# CONFIG_MAIN_TABLE
# CONFIG_MAP_ANNOTATION_TABLE
# CONFIG_MAP3D_DISPLAY_TABLE
# CONFIG_MAP3D_VIEW_TABLE
# CONFIG_PANE_TABLE
# CONFIG_PASO_SETTINGS_TABLE
# CONFIG_PHASE_TABLE
# CONFIG_REF_ANNOTATION_TABLE
# CONFIG_RIPPLE_MAPPING_PREFERENCE_TABLE
# CONFIG_STIMULATION_TABLE
# CONFIG_TEMPERATURES_PREFERENCE_TABLE
# CONFIG_TGA_PRESET_TABLE
# CONFIG_VISI_TAG_PREFERENCE_TABLE
# CONFIG_VISI_TAG_PRESET_TABLE
# CONFIG_WINDOW_SETTINGS_TABLE
# CONNECTOR_FILTER_TABLE
# CS_COORD_SYSTEM_TABLE
# DATABASE_VERSION
# DICOM_DIR_TABLE
# DICOM_II_TABLE
# ECG_PATTERNS_TABLE
# ECG_PRESET_PARAMETERS_TABLE
# ECG_PRESETS_TABLE
# ECG_STUDY_PRESET_PARAMETERS_TABLE
# ECG_STUDY_WINDOW_PRESET_PARAMETERS_TABLE
# GENERIC_SETUP_TABLE
# MAP_ANNOTATION_MAP_SETUP_TABLE
# MAPS_TABLE
# PASO_IS_IS_SIGNALS_CORR_TABLE
# PASO_IS_TABLE
# PASO_PM_IS_SIGNALS_CORR_TABLE
# PASO_PM_TABLE
# PATIENTS_TABLE
# PHYSICIANS_TABLE
# POINT_GROUPS_TABLE
# POINTS_TABLE
# PRESET_FILTER_TABLE
# PROCEDURES_TABLE
# REF_ANNOTATION_MAP_SETUP_TABLE
# RF_TABLE
# SCAR_TABLE
# SECONDARY_WINDOWS_POSITIONS
# SEGMENTED_VOLUME_TABLE
# SETUP_TABLE
# STUDIES_TABLE
# STUDY_BACKUP_COMMIT_FILES_TABLE
# STUDY_BACKUP_HISTORY_TABLE
# STUDY_BACKUP_INFO_TABLE
# STUDY_RECORDINGS_TABLE
# TAG_SETUP_TABLE
# TRIAL_LICENSE_TABLE
# ULS_ANNOTATIONS_TABLE
# ULS_CLIPS_TABLE
# ULS_CONTOURS_TABLE
# ULS_FRAMES_POSITIONS_TABLE
# ULS_FRAMES_TABLE
# ULS_GATED_FRAMES_TABLE
# ULS_POINTS_TABLE
# ULS_TAGS_PER_CONTOUR_TABLE
# USED_LICENSE_TABLE
# VIEW_SETUP_TABLE
# VOLUME_TABLE
