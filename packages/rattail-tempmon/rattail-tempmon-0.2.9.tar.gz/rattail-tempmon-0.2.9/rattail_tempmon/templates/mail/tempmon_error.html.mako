## -*- coding: utf-8 -*-
<html>
  <body>
    <p>At ${taken or now}, ${probe} reported that its status was: ${status}.<br>
      Something went wrong. Please investigate as soon as possible.
    </p>
    <p>This email will repeat every ${probe.status_alert_timeout} minutes until the issue is resolved.
    </p>
  </body>
</html>
