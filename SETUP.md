# Setup

## Install dependencies
```
pip install -r requirements.txt
```

## Google Cloud Storage
Set the environment variable with the path to your credentials:
```
export GOOGLE_APPLICATION_CREDENTIALS="key.json"
```

## Adding `polkit` rules
Add the following lines to `/etc/polkit-1/rules.d/mount.rules`, and replace `user` with your username:
```
polkit.addRule(function(action, subject) {
	if ((
		action.id == "org.freedesktop.udisks2.filesystem-mount" ||
		action.id == "org.freedesktop.udisks2.filesystem-unmount" ||
		action.id == "org.freedesktop.udisks2.filesystem-mount-other-seat" ||
		action.id == "org.freedesktop.udisks2.power-off-drive-other-seat" ||
		action.id == "org.freedesktop.udisks2.eject-media"
		) && subject.user == "user"
	)
	{
		return polkit.Result.YES;
	}
});
```
Add the following lines to `/etc/polkit-1/rules.d/login.rules`:
```
polkit.addRule(function(action, subject) {
	if ((
		action.id == "org.freedesktop.login1.reboot" ||
		action.id == "org.freedesktop.login1.reboot-multiple-sessions" ||
		action.id == "org.freedesktop.login1.power-off" ||
		action.id == "org.freedesktop.login1.halt" ||
		action.id == "org.freedesktop.login1.power-off-multiple-sessions"
		) && subject.user == "user"
	)
	{
		return polkit.Result.YES;
	}
});
```
Add the following lines to `/usr/share/polkit-1/actions/org.audiograbd.wakealarm.policy`:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
  "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
  "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <action id="org.audiograbd.wakealarm">
    <description>Set RTC wake alarm</description>
    <message>Set RTC wake alarm</message>
    <defaults>
      <allow_any>no</allow_any>
      <allow_inactive>no</allow_inactive>
      <allow_active>no</allow_active>
    </defaults>
  </action>
</policyconfig>
```

Add the following lines to `/etc/polkit-1/rules.d/wakealarm.rules`:
```
polkit.addRule(function(action, subject) {
    if (action.id === "org.audiograbd.wakealarm" &&
        subject.user === "user") {
        return polkit.Result.YES;
    }
});
```




## GPIO Access
To use GPIO, `gpiozero` requires access to `/dev/mem`. Add yourself to the `kmem` group:
```
sudo usermod -aG kmem "user"
``` 

## Wakealarm helper
Set permissions:
```
sudo chmod 755 /usr/local/bin/wakealarm
chown root:root /usr/local/bin/wakealarm
```