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
And add the following lines to `/etc/polkit-1/rules.d/login.rules`:
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

## Install `wakectl`
Compile:
```
gcc wakectl.c -o wakectl
```
Move the binary to `/usr/local/bin`:
```
sudo mv wakectl /usr/local/bin/
```
Change the ownership of `wakectl` to `root`:
```
sudo chown root:root /usr/local/bin/wakectl
```
Set permissions:
```
sudo chmod 4755 /usr/local/bin/wakectl
```
