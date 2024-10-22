# ------------ Importing Libraries ------------

import arcpy
import pandas as pd
import smtplib, ssl
from datetime import datetime
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import os

# ------------ Updaters Credentials ------------

username = "username" # ArcGIS Online username
password = "password" # ArcGIS Online password
data_check = "MH" # Initials
receiver_email = "emorgan2@anglianwater.co.uk" # Email to recieve update on code completion

# ------------ Accessing ArcGIS Online ------------

print("Authenticating to ArcGIS Online...")
try:
    gis = GIS("https://www.arcgis.com", username, password)
    print(f"Successfully authenticated as: {gis.users.me.username}")
except Exception as auth_error:
    print(f"Failed to authenticate: {auth_error}")
    exit()

# ------------ Establishing AGOL Hosted Feature Layer URLS and Name Mapping ------------

gdb_feature_layer_urls = [
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/4",
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/5",
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/6"
]

url_to_name_mapping = {
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/4": "Area",
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/5": "Lines",
    "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/Test_Alliance_Shared_Mark_ups_and_Annotations_V2_COPY/FeatureServer/6": "Points"
}

# ------------ Establishing AGOL Hosted Table URLS ------------

hosted_table_url = "https://services3.arcgis.com/VCOY1atHWVcDlvlJ/arcgis/rest/services/projects_info_copy_3/FeatureServer/0"
hosted_table = FeatureLayer(hosted_table_url)
query_result = hosted_table.query(where="1=1", out_fields="*", return_geometry=False)
table_data = query_result.sdf

# ------------ Establishing Output csv ------------

log_csv_output_path = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Data Cleansing\UpdateLog\UpdateLogTest.csv"

# ------------ Establishing Script Logging ------------

update_log = []
current_date = datetime.now()

def log_update(feature_layer, project_code, object_id=None, old_project_name=None, new_project_name=None,
               old_investment=None, new_investment=None, old_dm_stage=None, new_dm_stage=None,
               old_construction_stage=None, new_construction_stage=None):
    update_log.append({
        "Feature Layer": feature_layer,
        "ProjectCode": project_code,
        "OBJECTID": object_id,
        "Old Project Name": old_project_name,
        "New Project Name": new_project_name,
        "Old Investment": old_investment,
        "New Investment": new_investment,
        "Old DM Stage": old_dm_stage,
        "New DM Stage": new_dm_stage,
        "Old Construction Stage": old_construction_stage,
        "New Construction Stage": new_construction_stage,
        "Data Check": data_check,
        "Data Check Date": datetime.now().strftime('%d/%m/%Y')
    })

# ------------ Establishing Email Notification ------------

def send_email_notification(status="Success", update_log=None, error_details=None):
    sender_email = "datacleansingpythonscript@gmail.com"
    sender_password = "eayb uqdu zrxc wvkt"
    port = 465
    smtp_server = "smtp.gmail.com"
    subject = f"Python Script: {status} Notification"

    if status == "Success":
        if update_log:
            df_log = pd.DataFrame(update_log)
            html_table = df_log.to_html(index=False, border=1, justify='center', col_space=5)
            body = f"""
            <html>
            <body>
                <p>The cleansing script completed successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>
                <p>Updates were made to the following feature layers:</p>
                {html_table}
            </body>
            </html>
            """
        else:
            body = f"""
            <html>
            <body>
                <p>The cleansing script completed successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>
                <p>No updates were necessary during this run.</p>
            </body>
            </html>
            """
    else:
        body = f"""
        <html>
        <body>
            <p>The cleansing script failed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>
            <p>Error Details:</p>
            <p>{error_details}</p>
        </body>
        </html>
        """

    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content("This is a plain text version of the email.", subtype="plain")
    em.add_alternative(body, subtype="html") 

    if status == "Success" and update_log:
        with open(log_csv_output_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(log_csv_output_path)}")
            em.add_attachment(part)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(em)
        print(f"{status} notification email sent successfully.")
    except Exception as e:
        print(f"Failed to send notification email: {e}")

# ------------ Function 1: Updating Project Name ------------

def update_project_name():
    for gdb_feature_layer_url in gdb_feature_layer_urls:
        print(f"Processing Feature Layer: {gdb_feature_layer_url}")

        with arcpy.da.UpdateCursor(gdb_feature_layer_url, ["OBJECTID", "ProjectCode", "ProjectName", "DataCheck", "DataCheckDate"]) as cursor:
            for row in cursor:
                object_id = row[0]
                project_code = row[1]

                match = table_data[table_data['SAPNoP6'] == project_code]
                if not match.empty:
                    new_project_name = match['ProjectName'].values[0]
                    if row[2] != new_project_name:
                        old_project_name = row[2]
                        row[2] = new_project_name
                        row[3] = data_check
                        row[4] = current_date
                        cursor.updateRow(row)
                        log_update(url_to_name_mapping[gdb_feature_layer_url], project_code, object_id,
                                   old_project_name=old_project_name, new_project_name=new_project_name)

# ------------ Function 2: Updating Investment Code ------------

def update_investment():
    for gdb_feature_layer_url in gdb_feature_layer_urls:
        print(f"Processing Feature Layer: {gdb_feature_layer_url}")

        with arcpy.da.UpdateCursor(gdb_feature_layer_url, ["OBJECTID", "ProjectCode", "InvestmentID", "DataCheck", "DataCheckDate"]) as cursor:
            for row in cursor:
                object_id = row[0]
                project_code = row[1]

                match = table_data[table_data['SAPNoP6'] == project_code]
                if not match.empty:
                    new_investment_name = match['ProjectRef'].values[0]
                    if row[2] != new_investment_name:
                        old_investment_name = row[2]
                        row[2] = new_investment_name
                        row[3] = data_check
                        row[4] = current_date
                        cursor.updateRow(row)
                        log_update(url_to_name_mapping[gdb_feature_layer_url], project_code, object_id,
                                   old_investment=old_investment_name, new_investment=new_investment_name)

# ------------ Function 3: Updating DM Dates ------------

def determine_dm_stage(row, current_date):
    if pd.isna(row['P6DM0FCACTDate']):
        return None
    elif current_date < row['P6DM0FCACTDate']:
        return 'DM0'
    elif row['P6DM0FCACTDate'] <= current_date < row['P6DM1FCACTDate']:
        return 'DM0'
    elif current_date == row['P6DM1FCACTDate']:
        return 'DM1'
    elif row['P6DM1FCACTDate'] < current_date < row['P6DM2FCACTDate']:
        return 'DM1'
    elif current_date == row['P6DM2FCACTDate']:
        return 'DM2'
    elif row['P6DM2FCACTDate'] < current_date < row['P6DM3FCACTDate']:
        return 'DM2'
    elif current_date == row['P6DM3FCACTDate']:
        return 'DM3'
    elif row['P6DM3FCACTDate'] < current_date < row['P6DM4FCACTDate']:
        return 'DM3'
    elif current_date == row['P6DM4FCACTDate']:
        return 'DM4'
    else:
        return 'DM4'

def update_dm_stage():
    date_columns = ['P6DM0FCACTDate', 'P6DM1FCACTDate', 'P6DM2FCACTDate', 'P6DM3FCACTDate', 'P6DM4FCACTDate']
    for col in date_columns:
        table_data[col] = pd.to_datetime(table_data[col], errors='coerce', format='%d/%m/%Y')

    for gdb_feature_layer_url in gdb_feature_layer_urls:
        print(f"Processing Feature Layer: {gdb_feature_layer_url}")

        with arcpy.da.UpdateCursor(gdb_feature_layer_url, ["OBJECTID", "ProjectCode", "DMStage", "DataCheck", "DataCheckDate"]) as cursor:
            for row in cursor:
                object_id = row[0]
                project_code = row[1]

                match = table_data[table_data['SAPNoP6'] == project_code]
                if not match.empty:
                    new_dm_stage = determine_dm_stage(match.iloc[0], current_date)
                    if new_dm_stage and row[2] != new_dm_stage:
                        old_dm_stage = row[2]
                        row[2] = new_dm_stage
                        row[3] = data_check
                        row[4] = current_date.strftime('%d/%m/%Y')
                        cursor.updateRow(row)
                        log_update(url_to_name_mapping[gdb_feature_layer_url], project_code, object_id,
                                   old_dm_stage=old_dm_stage, new_dm_stage=new_dm_stage)

# ------------ Function 4: Updating Construction Stage ------------

def determine_construction_stage(row, current_date):
    if pd.isna(row['P6ConStFCACTDate']) or pd.isna(row['P6ConFnFCACTDate']):
        return None
    if current_date < row['P6ConStFCACTDate']:
        return 'Pre-Construction'
    elif row['P6ConStFCACTDate'] <= current_date < row['P6ConFnFCACTDate']:
        return 'During Construction'
    elif current_date == row['P6ConFnFCACTDate']:
        return 'Post-construction'
    else:
        return 'Post-construction'

def update_construction_stage():
    date_columns = ['P6ConStFCACTDate', 'P6ConFnFCACTDate']
    for col in date_columns:
        table_data[col] = pd.to_datetime(table_data[col], errors='coerce', format='%d/%m/%Y')

    current_date = datetime.now()

    for gdb_feature_layer_url in gdb_feature_layer_urls:
        print(f"Processing Feature Layer: {gdb_feature_layer_url}")

        with arcpy.da.UpdateCursor(gdb_feature_layer_url, ["OBJECTID", "ProjectCode", "ConstructionStage", "DataCheck", "DataCheckDate"]) as cursor:
            for row in cursor:
                object_id = row[0]
                project_code = row[1]

                match = table_data[table_data['SAPNoP6'] == project_code]
                if not match.empty:
                    new_dm_stage = determine_construction_stage(match.iloc[0], current_date)
                    if new_dm_stage and row[2] != new_dm_stage:
                        old_dm_stage = row[2]
                        row[2] = new_dm_stage 
                        row[3] = data_check
                        row[4] = current_date.strftime('%d/%m/%Y')
                        cursor.updateRow(row)
                        log_update(url_to_name_mapping[gdb_feature_layer_url], project_code, object_id, 
                                   old_construction_stage=old_dm_stage, new_construction_stage=new_dm_stage)

# ------------ Executing Script and Sending Update Email ------------

def main():
    update_project_name()
    update_investment()
    update_dm_stage()
    update_construction_stage()

    if update_log:
        update_log_df = pd.DataFrame(update_log)
        update_log_df.to_csv(log_csv_output_path, index=False)
        print(f"\nUpdate log successfully saved to: {log_csv_output_path}")
    else:
        print("\nNo updates were made during this session.")


try:
    update_log = []

    print("Authenticating to ArcGIS Online...")
    gis = GIS("https://www.arcgis.com", username, password)
    print(f"Successfully authenticated as: {gis.users.me.username}")

    update_project_name()
    update_investment()
    update_dm_stage()
    update_construction_stage()

    if update_log:
        pd.DataFrame(update_log).to_csv(log_csv_output_path, index=False)
        print(f"\nUpdate log successfully saved to: {log_csv_output_path}")
    else:
        print("No updates were made.")

    send_email_notification(status="Success", update_log=update_log)

except Exception as e:
    print(f"Script failed: {e}")
    send_email_notification(status="Failure", error_details=str(e))
