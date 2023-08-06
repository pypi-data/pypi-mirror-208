# Sleepytime

A simple gui that can prompt you to hibernate your computer. Use task scheduler to have it prompt you at night.
If you click delay, it'll sleep an hour and prompt you again.

If you delay and want to exit, right click the system tray icon and hit exit.

Right now this only works on Windows... PRs are welcome for other OSes.

# GUI
![GUI](gui.png "GUI Example")

## To Run:

Download a release exe (built via Github Actions!).. then run via

```
sleepytime.exe
```

Or if you have Python 3.10 or greater already:

```
# install once
pip install sleepytime

# run as often as you'd like after
python -m sleepytime
```
