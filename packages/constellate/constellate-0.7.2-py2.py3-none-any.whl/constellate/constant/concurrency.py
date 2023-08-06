import psutil

# CPU cores
_process = psutil.Process()

LOGICAL_CPUS_COUNT = (
    len(_process.cpu_affinity())
    if hasattr(_process, "cpu_affinity")
    else psutil.cpu_count(logical=True)
)
