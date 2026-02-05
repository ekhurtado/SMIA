import os
import csv

from smia import GeneralUtils
from smia.logic import acl_smia_messages_utils


async def save_csv_neg_metrics_timestamp(folder_path, agent_jid, neg_num=None, neg_thread=None,
                                         description=None, file_prefix=None):

    agent_jid = await acl_smia_messages_utils.get_agent_id_from_jid(agent_jid)
    # Add ‘N/A’ if optional variables have not been specified
    neg_num, neg_thread, description, file_prefix = [v if v is not None else "N/A" for v in
                                                     (neg_num, neg_thread, description, file_prefix)]

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)  # If necessary, the folder is created

    file_path = f"{folder_path}/{file_prefix}{agent_jid}-metrics.csv"
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['AgentID', 'Timestamp', 'NegotiationNum', 'NegotiationThread', 'Description'])
            writer.writerow([f"{agent_jid}", f"{GeneralUtils.get_current_timestamp_microsecs():.4f}", f"{neg_num}",
                             f"{neg_thread}", f"{description}"])
    except Exception as e:
        print(f"Error writing to file: {e}")

async def save_ready_csv_metrics_timestamp(self, folder_path):

    agent_jid = await acl_smia_messages_utils.get_agent_id_from_jid(self.myagent.jid)
    description = 'SMIA NR all negotiations requested'
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)  # If necessary, the folder is created

    file_path = f"{folder_path}/ready-{agent_jid}-metrics.csv"
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['AgentID', 'Timestamp', 'Description'])
            writer.writerow(
                [f"{agent_jid}", f"{GeneralUtils.get_current_timestamp_microsecs():.4f}", f"{description}"])
    except Exception as e:
        print(f"Error writing to file: {e}")
