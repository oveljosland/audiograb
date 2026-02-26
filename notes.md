# notes

## access to udisks2 and shutdown
udisksctl needs password to mount/unmount - add polkit rule.

put in ``/etc/polkit-1/rules.d/mount.rules`` and replace `user`,

```
polkit.addRule(function(action, subject) {
	if ((
		action.id == "org.freedesktop.udisks2.filesystem-mount" ||
		action.id == "org.freedesktop.udisks2.filesystem-unmount" ||
		action.id == "org.freedesktop.udisks2.eject-media"
		) && subject.user == "user"
	)
	{
		return polkit.Result.YES;
	}
});
```

put in ``/etc/polkit-1/rules.d/login.rules`` and replace `user`,
```
polkit.addRule(function(action, subject) {
	if ((
		action.id == "org.freedesktop.login1.reboot" ||
		action.id == "org.freedesktop.login1.reboot-multiple-sessions" ||
		action.id == "org.freedesktop.login1.power-off" ||
		action.id == "org.freedesktop.login1.power-off-multiple-sessions"
		) && subject.user == "user"
	)
	{
		return polkit.Result.YES;
	}
});
```

sudo chmod 644 /etc/polkit-1/rules.d/50-user-mount-umount.rules

## access to ``eeprom-config''
Edit ``sudo visudo`` and add
```deployuser ALL=(root) NOPASSWD: /usr/bin/rpi-eeprom-config, /usr/bin/rpi-eeprom-update```

## scheduling the next wake time
Write scheduler ----> C program (helper with some privileges) ????
```
# set wake interval in minutes
def set_interval(config):
	if not config["scheduler"]["enabled"]:
		return
	minutes = config["scheduler"]["interval_minutes"]
	output = subprocess.run(["wakectl", minutes*60])
```

## install wakectl
gcc wakectl.c -o wakectl
sudo mv wakectl /usr/local/bin/
sudo chown root:root /usr/local/bin/wakectl
sudo chmod 4755 /usr/local/bin/wakectl 
