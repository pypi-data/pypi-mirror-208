## -*- coding: utf-8 -*-
<html>
  <body>
    <p><b>This is a warning from ${probe}.</b><br>
      The status of ${probe} is: ${status}.<br>
      This is because the temperature is ${reading.degrees_f}<br>
      and has been so for longer than expected.<br>
      This unit should be looked at as soon<br>
      as possible to ensure no food goes to waste.
    </p>
    <p>
      Notes:<br>
      This alert will happen every ${probe.status_alert_timeout} minutes until<br>
      the temperature reaches an acceptable level.<br>
    </p>
  </body>
</html>
