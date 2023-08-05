import time

global tstart
tstart = None


def tic():
    """Starts a timer, ended by toc()"""
    global tstart
    if tstart is not None:
        raise Exception("tic() called with another tic() active!")
    tstart = time.perf_counter_ns()


def toc():
    """Ends the timer, returns the elapsed time"""
    global tstart
    if tstart is None:
        raise Exception("toc() called without an active tic()!")
    tend = time.perf_counter_ns()
    telapsed = (tend - tstart) / 1e9
    print(f"Elapsed time: {telapsed:.2e} seconds")
    tstart = None
    return telapsed
