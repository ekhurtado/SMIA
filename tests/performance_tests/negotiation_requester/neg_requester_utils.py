import os
import csv
import time

from smia.utilities.general_utils import DockerUtils

from smia.logic import acl_smia_messages_utils


async def save_csv_neg_metrics(folder_path, participants, parallel_negs, neg_iter, experiment_iter, experiment_id,
                               elapsed_time):

    # Add ‘N/A’ if optional variables have not been specified
    participants, parallel_negs, neg_iter, experiment_iter, experiment_id, elapsed_time = \
        [v if v is not None else "N/A" for v in
         (participants, parallel_negs, neg_iter, experiment_iter, experiment_id, elapsed_time)]

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)  # If necessary, the folder is created

    file_path = f"{folder_path}/test_{participants}_{parallel_negs}_negs.csv"
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['FactorA', 'FactorB', 'NegIteration', 'ExperimentIteration', 'ExperimentID',
                                 'ElapsedTime'])
            writer.writerow([f"{participants}", f"{parallel_negs}", f"{neg_iter}", f"{experiment_iter}",
                             f"{experiment_id}", f"{elapsed_time / 1e9:.9f}"])
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
                [f"{agent_jid}", f"{get_current_timer_nanosecs():.9f}", f"{description}"])
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


def get_safe_env_var(key, default, var_type):
    """
    Gets an environment variable, converts it to the desired type, and returns the default if it fails or does not
    exist.

    """
    try:
        value = DockerUtils.get_env_var(key)
        return var_type(value)
    except (TypeError, ValueError, AttributeError):
        return default
