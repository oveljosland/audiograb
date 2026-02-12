# notes

## access to udisks2
udisksctl needs password to mount/unmount - add polkit rule.

put in ``/etc/polkit-1/rules.d/50-user-mount-umount.rules``,

```
polkit.addRule(function(action, subject) {
	if ((action.id == "org.freedesktop.udisks2.filesystem-mount" ||
		action.id == "org.freedesktop.udisks2.filesystem-unmount" ||
		action.id == "org.freedesktop.udisks2.eject-media") &&
		subject.user == "user") {
			return polkit.Result.YES;
		}
});
```

sudo chmod 644 /etc/polkit-1/rules.d/50-user-mount-umount.rules

## access to ``eeprom-config''
Edit ``sudo visudo`` and add
```deployuser ALL=(root) NOPASSWD: /usr/bin/rpi-eeprom-config, /usr/bin/rpi-eeprom-update```

## scheduling the next wake time
Write scheduler ----> C program ????