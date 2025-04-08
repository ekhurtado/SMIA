import csv
import os
import time


def safe_metrics(start, finish, elapsed_time):

    try:
        file_path = './my_metrics.csv'
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                writer.writerow(['Start', 'Finish', 'ElapsedTime'])
            writer.writerow([f"{start:.4f}", f"{finish:.4f}", f"{elapsed_time:.4f}"])
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    start = time.time()

    # Simula alguna operación (por ejemplo, una pausa de 2 segundos)
    time.sleep(4)

    # Marca el final
    finish = time.time()

    startup_time = finish - start
    print("Time between {} and {} has been {}s".format(start, finish, startup_time))
    safe_metrics(start, finish, startup_time)



if __name__ == "__main__":
    main()