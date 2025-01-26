# Part Selector Tool
<!---
..
    fender-bender readthedocs documentation

    by:   x0pherl
    date: September 25th 2024

    desc: This is the documentation for the fender-bender filament buffering solution on readthedocs

    license:

        Copyright 2024 x0pherl

        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->


## Select Parts

While a standard fender-bender assembly requires 12 distinct parts, there are many different combinations that can be chosen to meet your exact needs. As of v2 there are over 90 distinct parts!

This guide is intended to help you build a print-list for your unique needs.

<link rel="stylesheet" href="https://unpkg.com/tippy.js@6/dist/tippy.css">
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script src="https://unpkg.com/tippy.js@6"></script>

<form id="parts-form">
  <label for="flow-direction" id="flow-direction-label">Flow Directions:</label>
  <select id="flow-direction" name="flow-direction">
    <option value="forward">Forward</option>
    <option value="straight">Straight</option>
    <option value="reverse">Reverse</option>
  </select>
  <br><br>

  <label for="connector" id="connector-label">Connector / Tubing Choice:</label>
  <select id="connector" name="connector">
    <option value="3mmx6mm">6mmODx3mmID Tubing with no connector</option>
    <option value="3mmx6mm-pc6-01">6mmODx3mmID Tubing with PC6-01 Connectors</option>
    <option value="2_5mmx4mm">4mmODx2.5mmID Tubing with no connector</option>
    <option value="2_5mmx4mm-pc4-m10">4mmODx2.5mmID Tubing with PC4-M10 Connectors</option>
    <option value="2mmx4mm">4mmODx2mmID Tubing with no connector</option>
    <option value="2mmx4mm-pc4-m10">4mmODx2mmID Tubing with PC4-M10 Connectors</option>
  </select>
  <br><br>

  <label for="filament-count" id="filament-count-label">Filament Count:</label>
  <select id="filament-count" name="filament-count">
    <option value=5>5 filament channels (select for Prusa MMU)</option>
    <option value=8>8 filament channels</option>
    <option value=12>12 filament channels</option>
  </select>
  <br><br>

  <label for="frame-style" id="frame-style-label">Frame Style:</label>
  <select id="frame-style" name="frame-style">
    <option value="hanging">Hanging</option>
    <option value="standing">Standing</option>
    <option value="hybrid">Hybrid</option>
  </select>
  <br><br>

  <label for="wall-style" id="wall-style-label">Wall Style:</label>
  <select id="wall-style" name="wall-style">
    <option value="hex">Hex Pattern for maximum visibility</option>
    <option value="solid">Solid</option>
    <option value="drybox">Drybox (maintains some hex styling elements)</option>
  </select>
  <br><br>

  <label for="extras">Other Features:</label>
  <br>
  <input type="checkbox" id="pip-bearing" name="pip-bearing" value="pip-bearing">
  <label for="pip-bearing" id="pip-bearing-label"> Print-in-place Wheel Bearing (not recommended)</label><br>
  <input type="checkbox" id="surface-mount" name="surface-mount" value="surface-mount">
  <label for="surface-mount" id="surface-mount-label"> Surface-Mount Hanger (geneally requires "Reverse" Filament Flow Direction)</label><br>
  <input type="checkbox" id="surface-mount-heatsink" name="surface-mount-heatsink" value="surface-mount-heatsink">
  <label for="surface-mount-heatsink" id="surface-mount-heatsink-label"> Use Heatsink in Surface-Mount Hanger</label><br><br>

  <input type="button" value="Generate Parts List" onclick="generatePartsList()">
</form>


<!-- Hidden help text -->
<div id="flow-direction-help" style="display: none;">
  <p>Ideally, your fender-bender should be installed in a location that creates a straight path to your filament rolls, and to your printer. This significantly reduces friction in the system.</p>
  <p>Our default design assumes that you will have a wall mounted buffer with the filaments suspended above. The buffer will be installed with the hanger slightly below the level of the printer, ensuring that there is a straight line from the 45 degree exit of the filament bracket to the back of the printer.</p>
  <p>However, this solution may not be practical in all circumstances. You may, for example, want to suspend the filament buffer from the back of a wheeled table or cart, with the filament mounted in a frame above the printer.</p>
  <p><strong>Forward (Default):</strong>The path closest to the bracket mount extends in a straight vertical line, the path farthest from the bracket extends outward at a 45º angle</p>
  <p><strong>Straigth:</strong>Both paths extend in a straight vertical line.</p>
  <p><strong>Reverse:</strong>The path closest to the bracket mount extends outward at a 45º angle, the path farthest from the bracket extends in a straight vertical line.</p>
</div>

<div id="connector-help" style="display: none;">
  <p>Fender-Bender supports many options for connectors to hold your tubing securely in place, as well as no connector (which is our default design). While not conventionally used in 3d printing applications, 6mm outer diameter tubing adds significant strength while reducing friction.</p>
  <p>The tubing options show both OD (outer diameter) and ID (inner diameter) measurements. The connector types shown are standard push-through connector sizes which will alow the tubing to be securely locked into place.</p>
</div>

<div id="filament-count-help" style="display: none;">
  <p>Determines how many separate filament channels are generated for the external wall parts.</p>
  <p>The Prusa MMU system supports five filament channels; common ERCF kits support 8 or 12 channels</p>
</div>

<div id="frame-style-help" style="display: none;">
  <p><strong>Hanging: </strong> Adds additional horizontal spacing to the frame components to support the interlocking frame hanger. Has a rounded bottom which is lightweight an elegant; but cannot stand on its own. Additionally, there is no "drybox" version of the bottom hanging bracket.</p>
  <p><strong>Standing: </strong> The standing design slightly reduces the overall length to reduce filament usage, and removes the back cutout for the hanging bracket.</p>
  <p><strong>Hybrid: </strong> Combines the strengths of the two systems. Adds additional horizontal spacing to the frame components to support the interlocking frame hanger, and maintains the cutout on the top frame for the hanging bracket, but adds a frame to the bottom which supports drybox configurations and allows the system to stand on a flat surface.</p>
</div>

<div id="wall-style-help" style="display: none;">
  <p><strong>Hex: </strong> A hexagonal pattern that allows for maximum visibility when troubleshooting filament flow issues.</p>
  <p><strong>Solid: </strong> All wall parts are solid, simple geometries. Provides full isolation between channels and reduces filament consumption for the fender-bender itself, but eliminates visibility to the system.</p>
  <p><strong>Drybox: </strong> Adds a thin barrier to external parts while maintaining some of the hexwall styling. Eliminates visibility to the system.Note: selecting this will also change the bottom bracket choice, in order to maintain the seal.</p>
</div>

<div id="pip-bearing-help" style="display: none;">
  <p>If you don't want to purchase bearings, or they're unavailable in your area; we've included a print-in-place bearing design for the filament wheel. This will not be as durable or as smooth as a proper bearing, so it's not generally recommended.</p>
</div>

<div id="surface-mount-help" style="display: none;">
  <p>A surface mounted installation allows you to hang the filament buffer directly from a desktop or tabletop surface. This installation method on a rolling desk can make changing filaments signficantly easier, especially if you're able to mount a filament hanger to the desk surface as well.</p>
  <p>M4 bolts and nuts (or heatsinks) are required for installation.</p>
</div>

<div id="surface-mount-heatsink-help" style="display: none;">
  <p>If you prefer heatsinks to M4 nuts, choose this option.</p>
</div>

<h3>Parts List</h3>
<ul id="parts-list"></ul>

<script>

function replaceRepeats(repeat, source) {
  const regex = new RegExp(`(${repeat})+`, 'g');
  const result = source.replace(regex, repeat);
  return result;
}

function generatePartsList() {
  var flowDirection = document.getElementById("flow-direction").value;
  var connector = document.getElementById("connector").value;
  var filamentCount = document.getElementById("filament-count").value;
  var frameStyle = document.getElementById("frame-style").value;
  var wallStyle = document.getElementById("wall-style").value;

  var partsList = document.getElementById("parts-list");
  partsList.innerHTML = "";

  var li = document.createElement("li");
  li.appendChild(document.createTextNode("<strong>Filament Clip (1x)</strong>: /filament-bracket-clip.stl"));
  partsList.appendChild(li);

  var bottom_fname = ""
  var top_fname = ""
  if (flowDirection == "forward") {
    if (connector != "3mmx6mm") {
      bottom_fname = bottom_fname + "/alt-brackets-"+flowDirection+"-path-angle-alternate-connectors";
      bottom_fname = bottom_fname + "/alt-filament-bracket-bottom-" + connector + ".stl"
      top_fname = top_fname + "/alt-brackets-"+flowDirection+"-path-angle-alternate-connectors";
      top_fname = top_fname + "/alt-filament-bracket-top-" + connector + ".stl"
      }
    else {
      bottom_fname = bottom_fname + "/filament-bracket-bottom.stl"
      top_fname = top_fname + "/filament-bracket-top.stl"
      }
    }
  else {
    bottom_fname = bottom_fname + "/alt-brackets-"+flowDirection+"-path-angle";
    top_fname = top_fname + "/alt-brackets-"+flowDirection+"-path-angle";
    if (connector != "3mmx6mm") {
      bottom_fname = bottom_fname + "/alt-brackets-"+flowDirection+"-path-angle-alternate-connectors";
      bottom_fname = bottom_fname + "/alt-filament-bracket-bottom-"+flowDirection+"-path-angle-" + connector + ".stl"
      top_fname = top_fname + "/alt-brackets-"+flowDirection+"-path-angle-alternate-connectors";
      top_fname = top_fname + "/alt-filament-bracket-top-"+flowDirection+"-path-angle-" + connector + ".stl"
      }
    else {
      bottom_fname = bottom_fname + "/alt-filament-bracket-bottom-"+flowDirection+"-path-angle.stl"
      top_fname = top_fname + "/alt-filament-bracket-top-"+flowDirection+"-path-angle.stl"
      }
    }

  var li = document.createElement("li");
  var description = "<strong>Bottom Filament Bracket (" + filamentCount + "x)</strong>: " + bottom_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

  var li = document.createElement("li");
  var description = "<strong>Top Filament Bracket (" + filamentCount + "x)</strong>: " + top_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

  wheel_fname = "/filament-bracket-wheel.stl"
  if (document.getElementById("pip-bearing").checked) {
    wheel_fname = "/alt-wheel-print-in-place-bearing/alt-filament-bracket-wheel-print-in-place-bearing.stl"
    }
  var li = document.createElement("li");
  var description = "<strong>Filament Bracket Wheel (" + filamentCount + "x)</strong>: " + wheel_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

  sidewall_base_fname = "wall-side"
  sidewall_base_dir = "/"
  if (wallStyle != "hex") {
    sidewall_base_dir = sidewall_base_dir + "alt-wall-styles/"
    sidewall_base_fname = "alt-" + sidewall_base_fname + "-" + wallStyle
  }
  sidewall_fname = sidewall_base_dir + sidewall_base_fname + ".stl"

  var li = document.createElement("li");
  var description = "<strong>Sidewall (" + (filamentCount - 1) + "x)</strong>: " + sidewall_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

  sidewall_base_fname = "wall-side-reinforced"
  sidewall_base_dir = "/"
  if (wallStyle != "hex") {
    sidewall_base_dir = sidewall_base_dir + "alt-wall-styles/"
    sidewall_base_fname = "alt-" + sidewall_base_fname + "-" + wallStyle
  }
  sidewall_fname = sidewall_base_dir + sidewall_base_fname + ".stl"

  var li = document.createElement("li");
  var description = "<strong>Reinforced Sidewall (2x)</strong>: " + sidewall_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

  guidewall_base_fname = "wall-guide"
  guidewall_base_dir = "/"
  if (filamentCount != 5) {
    guidewall_base_dir = guidewall_base_dir+"alt-"+filamentCount+"-filaments-parts/"
  }
  if (wallStyle != "hex") {
    guidewall_base_dir = guidewall_base_dir + "alt-wall-styles/"
    guidewall_base_fname = "alt-" + guidewall_base_fname + "-" + wallStyle
  }
  if (filamentCount != 5) {
    guidewall_base_fname = "alt-" + guidewall_base_fname + "-"+filamentCount+"-filaments"
  }
  guidewall_fname = replaceRepeats("alt-", guidewall_base_dir + guidewall_base_fname + ".stl")

  var li = document.createElement("li");
  var description = "<strong>Guidewall (2x)</strong>: " + guidewall_fname
  li.appendChild(document.createTextNode(description));
  partsList.appendChild(li);

// li = document.createElement("li");
  // li.appendChild(document.createTextNode("Material: " + material));
  // partsList.appendChild(li);

  // li = document.createElement("li");
  // li.appendChild(document.createTextNode("Color: " + color));
  // partsList.appendChild(li);

  // if (extras.length > 0) {
  //   li = document.createElement("li");
  //   li.appendChild(document.createTextNode("Extras: " + extras.join(", ")));
  //   partsList.appendChild(li);
  // }
  }

document.querySelectorAll('[id$="-label"]').forEach(function(label) {
  var helpId = label.id.replace('-label', '-help');
  var helpElement = document.getElementById(helpId);
  if (helpElement) {
    tippy(label, {
      content: helpElement.innerHTML,
      allowHTML: true,
      interactive: true,
      maxWidth: 300,
    });
  }
});

</script>