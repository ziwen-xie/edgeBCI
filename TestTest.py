import scipy.signal
from sklearn.metrics import mean_absolute_error as mae
from digitalfilter import LiveLFilter

# define lowpass filter with 2.5 Hz cutoff frequency
b, a = scipy.signal.iirfilter(4, Wn=2.5, fs=fs, btype="low", ftype="butter")
y_scipy_lfilter = scipy.signal.lfilter(b, a, yraw)

live_lfilter = LiveLFilter(b, a)
# simulate live filter - passing values one by one
y_live_lfilter = [live_lfilter(y) for y in yraw]

print(f"lfilter error: {mae(y_scipy_lfilter, y_live_lfilter):.5g}")
