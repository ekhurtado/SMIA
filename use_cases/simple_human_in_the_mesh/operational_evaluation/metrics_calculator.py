import csv
import os
import time


def safe_request_metrics(file_path, elapsed_time):
    import csv
    import os
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['RequestTime'])
            writer.writerow([f"{elapsed_time:.4f}"])
    except Exception as e:
        print(f"Error writing to file: {e}")

def safe_metrics(file_path, start, finish, elapsed_time):
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['Start', 'Finish', 'ElapsedTime'])
            writer.writerow([f"{start:.4f}", f"{finish:.4f}", f"{elapsed_time:.4f}"])
    except Exception as e:
        print(f"Error writing to file: {e}")


def read_csv_and_get_elapsed_times(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    start = row[0]
                    finish = row[1]
                    diff = float(finish) - float(start)
                    print(f"Difference between first and second start: {diff:.4f} seconds")

    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    # file_path = 'my_metrics.csv'
    file_path = 'metrics/requests_metrics.csv'

    start = time.time()

    # Simula alguna operación (por ejemplo, una pausa de 2 segundos)
    time.sleep(4)

    # Marca el final
    finish = time.time()

    startup_time = finish - start
    print("Time between {} and {} has been {}s".format(start, finish, startup_time))
    # safe_metrics(file_path, start, finish, startup_time)
    read_csv_and_get_elapsed_times(file_path)



if __name__ == "__main__":
    main()