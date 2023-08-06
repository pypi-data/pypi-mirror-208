# DEPRECATED - OVOS PHAL Notification and Widgets Plugin


This repository is no longer maintained by OpenVoiceOS, use https://github.com/OpenVoiceOS/ovos-gui-plugin-shell-companion instead

___________________________
The PHAL Plugin provides interfaces and API for OpenVoiceOS GUI notifications and widgets system. The notifications API supports 3 types of notification systems:

- Transient Notifications: A transient notification is displayed on the screen only for a specific period of time and it its not dismissed will be stored for the user to view the missed notification. A transient notification can be used by skills to inform the user of missed events like reminders and device notifications

- Stick Notifications: A sticky notification is displayed on the screen for an indefinite period, until the user manually decides to cancel the notification. A sticky notification is used when urgent attention is required from the user, this can be used for example by the system to inform the user when a system update is available.

- Controlled Notifcations: A controlled notification is used internally by skills and plugins to display and notify users of information with regards to certain operations. This notification must be used with *caution* and *controlled set of events* as it allows plugins and skills to dynamically change the data within the controlled notification user interface

This plugin also provides support for homescreen widget management, widgets currently supported here:
- Timer Widget
- Alarm Widget
- Media Widget

# Requirements
- This plugin has no external requirements

# Install
`pip install ovos-PHAL-plugin-notification-widgets`

# Event Details:

##### Notifications Management System

Plugin provides the central notification management system in OpenVoice OS, it is responsible for storage, display request, dismissal request and storage remove request.

- Provides GUI ListView model for stored notifications:
```python
       # "ovos.notification.api.request.storage.model"
```

- API call to set the notification type and notification data
``` python
        # "ovos.notification.api.set"
```
  - API Notification set data format
    - Notes: Style can be four types ranging from info, warning, error and critical, each style has display colorset.

  ``` python
        example = {
                "sender": message.data.get("sender", ""),
                "text": message.data.get("text", ""),
                "action": message.data.get("action", ""),
                "type": message.data.get("type", ""),
                "style": message.data.get("style", "info")
        }
  ```

- API call to clear transient notification type
``` python
        # "ovos.notification.api.pop.clear"
```

- API call to clear and delete transient notification type
``` python
        # "ovos.notification.api.pop.clear.delete"
```

- API call to clear full storage db
``` python
        # "ovos.notification.api.storage.clear"
```

- API call to clear and delete single storage item
``` python
        # "ovos.notification.api.storage.clear.item"
```

- API call to set controlled notification display and data
``` python
        # "ovos.notification.api.set.controlled"
```
  - API Controlled Notification set data format:
  ``` python
        notification_message = {
                "sender": message.data.get("sender", ""),
                "text": message.data.get("text", ""),
                "style": message.data.get("style", "info")
        }
  ```

- API call to remove controlled notification
``` python
        # "ovos.notification.api.remove.controlled"
```

### Widgets Management System

Widgets system allows skills to display widgets on the homescreen, the management system is responsible for display, removal and updates of widgets

- API call to display widgets
``` python
   # "ovos.widgets.display"
   # Requires "data" and "type"
   # Example Request sent to widget API to display a timer:
   timerWidgetData = {"count": 1, "action":"ovos.gui.show.active.timers"}
   self.bus.on(Message("ovos.widgets.display", data={"type": "timer", "data": timerWidgetData}))
```

- API call to remove widgets
``` python
   # "ovos.widgets.remove"
   # Requires "data" and "type"
   # Example Request sent to widget API to remove a timer:
   self.bus.on(Message("ovos.widgets.remove", data={"type": "timer"}))
```

- API call to update widgets
``` python
   # "ovos.widgets.update"
   # Requires "data" and "type"
   # Example Request sent to widget API to update a timer count:
   timerWidgetData = {"count": 2}
   self.bus.on(Message("ovos.widgets.update", data={"type": "timer",  "data": timerWidgetData}}))
```
