import os
import csv
import time

from smia import GeneralUtils
from smia.logic import acl_smia_messages_utils


async def save_csv_neg_metrics_timestamp(folder_path, agent_jid, iteration=None, neg_thread=None,
                                         description=None, file_prefix=None):

    agent_jid = await acl_smia_messages_utils.get_agent_id_from_jid(agent_jid)
    # Add ‘N/A’ if optional variables have not been specified
    iteration, neg_thread, description = [v if v is not None else "N/A" for v in (iteration, neg_thread, description)]
    file_prefix = file_prefix or ''

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)  # If necessary, the folder is created

    file_path = f"{folder_path}/{file_prefix}{agent_jid}-metrics.csv"
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['AgentID', 'Timestamp', 'NegotiationNum', 'NegotiationThread', 'Description'])
            writer.writerow([f"{agent_jid}", f"{get_current_timer_nanosecs():.4f}", f"{iteration}",
                             f"{neg_thread}", f"{description}"])
    except Exception as e:
        print(f"Error writing to file: {e}")

async def save_prefix_csv_metrics_timestamp(folder_path, agent_jid, file_prefix=None):
    file_prefix = file_prefix or ''

    agent_jid = await acl_smia_messages_utils.get_agent_id_from_jid(agent_jid)
    description = 'SMIA NR all negotiations requested'
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)  # If necessary, the folder is created

    file_path = f"{folder_path}/{file_prefix}{agent_jid}-metrics.csv"
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['AgentID', 'Timestamp', 'Description'])
            writer.writerow(
                [f"{agent_jid}", f"{get_current_timer_nanosecs():.4f}", f"{description}"])
    except Exception as e:
        print(f"Error writing to file: {e}")




def get_current_timer_nanosecs():
    """
    This method returns the current high-resolution timer of the SMIA in nanoseconds as an integer.

    Returns:
        int: current timestamp in nanoseconds
    """
    # start_ns = time.perf_counter_ns()
    # await asyncio.sleep(5)
    # elapsed_ns = time.perf_counter_ns() - start_ns
    # _logger.assetinfo(f"9 decimales counter ns: {elapsed_ns / 1e9:.9f}")
    return time.perf_counter_ns()