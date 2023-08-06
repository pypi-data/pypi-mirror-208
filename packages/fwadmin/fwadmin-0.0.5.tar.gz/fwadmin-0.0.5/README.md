# FWAdmin

In the current alpha version, FWadmin allows to build EDLs referenced by firewalls. EDLs can be permanent, related to time-window frames or requested by users.

Components:

* DeviceGroup objects are a groups of Netbox devices.
* DynamicList objects are a group of DeviceGroup objects. They can be permanent (always on), related to time windows, or user requests. DynamicList objects build the EDL referenced by firewalls. Protocol, port and application are specified in the firewall rule referencing the EDL.
* Users can create Request objects for a specifc time frame referencing DynamicList objects.
