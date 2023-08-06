## -*- coding: utf-8; -*-
<html>
  <body>
    <h1>Disabled Tempmon Probes</h1>
    <p>
      We checked if there were any offline temperature probes at your location.&nbsp;
      Someone wanted these deactivated at some point, but you should make sure it is
      okay that they still are.&nbsp; Here are the results:
    </p>

    % if disabled_probes:
        <h3>Disabled Probes</h3>
        <ul>
          % for probe in disabled_probes:
              <li>${probe} (for client: ${probe.client.config_key})</li>
          % endfor
        </ul>
    % endif

    % if disabled_clients:
        <h3>Disabled Clients</h3>
        <ul>
          % for client in disabled_clients:
              <li>${client}</li>
          % endfor
        </ul>
    % endif

    <p>Please contact the Tech Department with any questions.</p>
  </body>
</html>
