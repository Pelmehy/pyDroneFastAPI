dock links:
flask: https://flask.palletsprojects.com/en/2.2.x/quickstart/
<br>
jinja: https://jinja.palletsprojects.com/en/3.0.x/templates/
<br>
adminLTE: https://adminlte.io/docs/3.2/

mavutil.py fix: <br>
path to file: C:\Users\Sarpness Home\AppData\Local\Programs\Python\Python39\Lib\site-packages\pymavlink\mavutil.py <br>
add command: <br><br>

self.mav.set_mode_send(self.target_system,
                               mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                               mode)
<br><br>
line: 680 end of <b>set_mode_apm</b> function
