## -*- coding: utf-8 -*-
<html>
  <body>
    <p>
      <b>This is an alert from ${probe}!</b><br>
      The status of ${probe} is: ${status}.<br>
      The current temperature is: ${reading.degrees_f}.<br>
      The temperature should never be this high.
      Investigate Immediately!<br>
    </p>
    <p>
      Notes: <br>
      Frozen food that is above 40 degrees needs to be thrown away<br>
      if it remains at that temperature for two hours or more.<br>
    </p>
    <p>
      Check out <a href="http://www.fsis.usda.gov/wps/portal/fsis/topics/food-safety-education/get-answers/food-safety-fact-sheets/safe-food-handling/freezing-and-food-safety/CT_Index/!ut/p/a1/jZFRT8IwEIB_DY9dbw7J8G1ZYtiUTYJK2Qsp7NYt2dqlrU759RZ8UQJK-9LefV-ud6UFZbSQ_L0R3DZK8vZwLyYbWMDEn8aQ5lP_HpLsdZE_xDGEy1sHrP8AsuBK_8KK4D8_vaLAjZ7Hc0GLntuaNLJSlAm0hEszoDaUVUqVxPAK7Sep-M4SUyNalzjEyDFbc1m2jRQO1oh7d3J6SX6YlMXPm0SW-EFXtPj9KvDdTrJgOZ6lWQD5-BQ4M7Zv4PJcXOOiVdvjH60juQ1C16HGCjVq7027cG1tb-5GMIJhGDyhlGjR26nunFArYyk74fruhe0foxk0T90qNNEXiOIqAA!!/#16">this USDA link</a> for useful information
    </p>
    <p>
      This email will repeat every ${probe.status_alert_timeout} minutes until the issue<br>
      has been resolved.
    </p>
    <p>
  </body>
</html>
