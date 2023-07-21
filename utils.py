import sys 
import os

def progressbar(it, prefix="", size=60, out=sys.stdout):
    #left for reference, but no longer needed
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


def resource_path(relative_path):
    """standardize relative references"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_int_date():
    import datetime
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")
run_number = get_int_date()
