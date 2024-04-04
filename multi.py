import multiprocessing
import subprocess     

def run_script(script_name):
    subprocess.call(["python", script_name])

if __name__ == "__main__":
    scripts = ["game.py", "webcam.py"]
    processes = []

    for script in scripts:
        process = multiprocessing.Process(target=run_script, args=(script,))
        processes.append(process)
        process.start()

    for process in processes: 
        process.join()
