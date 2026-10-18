# Credentials

User accounts and groups management on GNU/Linux Debian (Trixie - 13) distribution.

---

## Important Files to Retain
**`/etc/issue`**: Local pre-login banner.

**`/etc/issue.net`**: Remote SSH pre-login banner (legal warnings).In the SSH configuration file, **`/etc/ssh/sshd_config`**, remove the `#` comment symbol from the Banner line. If the value is set to none, replace it with **`/etc/issue.net`**: **Banner none → Banner /etc/issue.net** to configures `SSH` to display **`/etc/issue.net`** as a login banner before user's  authentication.

**`/etc/motd`**: Post-login message of the day.

**`/etc/login.defs`**: Configuration file of user and groups mechanism.

**`/etc/default/useradd`**: Useradd default configuration ( to see current configuration:  useradd -D).

**`/etc/skel`**: Skeleton of new user home directory.

**`/etc/subuid` and `/etc/subgid`**: Subordinate user and group IDs.

**`/etc/sudoers`**: The `sudo` policy file, always edit this file with the commmand `sudo visudo`.

## Root Login Case: `sudo` best practices

### `Sudo` Authentication Timestamp

> **Prefer creating configuration files in `/etc/sudoers.d/` rather than directly modifying `/etc/sudoers`.**

By default, `sudo` caches authentication credentials for **5 minutes**.

```bash
# Invalidates the current sudo authentication timestamp, next `sudo` command will ask for authentication again
sudo -k

# Removes the cached sudo credentials completely
sudo -K
```


### Configure the sudo timeout
> **sudoedit** utility is designed for editing privileged files without directly running the editor as root

In a sudoers file do:
```text
# env_reset: resets most environment variables when running a command with sudo, reducing the risk of environment-based privilege escalation.
# timestamp_timeout=5: after entering your password with sudo, the authentication is cached for 5 minutes. During that period, subsequent sudo commands usually won't ask for the password again
Defaults envreset, timestamptimeout=5

# Require authentication for every `sudo` command and uthentication timestamp never expires automatically.
Defaults timestamp_timeout=0

# Set the sudo authentication timeout to 30 minutes for a user `alice`:
Defaults: alice timestamp_timeout=30
```
---

### Check Sudo Privileges
> Prefer **`sudo <command>`** for traceability. Using **`su -`** or **`sudo su -`** opens a root shell, making individual actions harder to attribute to the original user
```bash
# Analyze sudo events
sudo journalctl _COMM=sudo
sudo journalctl -t -sudo

# Analyze authentification events
sudo journalctl -g "auth"

# Displays the commands and privileges granted to the current user through `sudo`.
sudo -l #check my current rights in sudoers file

# The default administrative group on Debian-based systems is sudo.
# On Red Hat-based systems (such as CentOS and Fedora), the administrative # group is typically wheel, following the traditional BSD convention.
# Add a user to the wheel group
sudo usermod -aG sudo bob

# Create a user with wheel membership:
sudo useradd -G sudo -m -d /home/<username> -s /bin/bash <username>

# Check the sudoers configuration
sudo visudo -c

# edit a specific sudoers file
sudo visudo -f <filename>
```

For a sudoers file like `/etc/sudoers`, use `visudo` and add:
```text
# Avoid:
# %sudo ALL=(ALL:ALL) NOPASSWD:ALL
# because it allows root privileges without requiring the user's password.

# Avoid:
# %sudo ALL=(ALL:ALL) ALL
# because members of sudo group to run all commands

# Miscellenaous sudoers file aliases:
# User_Alias
# Runas_Alias : target users/groups
# Host_Alias : machines and hosts
# Cmnd_Alias : commands
# example of using
DEVS ALL=(ALL) !/bin/su

# Avoid giving users unrestricted access to commands that can spawn a shell:
# /bin/bash, /bin/zsh, /bin/vim, /bin/awk , /bin/find, systemctl and similar
# powerful commands
# For example, instead of:
max ALL=(ALL) /bin/vim /etc/file

# prefer:
max ALL=(ALL) sudoedit /etc/file

# Be careful with commands such as:
alice ALL=(ALL:ALL) /usr/bin/systemctl status *

# Wildcards can grant more privileges than intended.
# Prefer restricting the target user/group and the exact command:
# This follows the principle of least privilege.

myke ALL=(<username>:<group>) <specific-command>

# A recommended step after completing the configuration is to lock the root password:
sudo passwd -l root

#To unlock the root password:
sudo passwd -u root

```
---

# Users and Groups

Be aware of `adduser` defaults. On some systems, new home directories may be created with permissions that are too permissive.

On Debian-based systems, check `/etc/adduser.conf` and consider:

`DIR_MODE=0700`

Also review password aging settings:

- `PASS_MAX_DAYS`
- `PASS_MIN_DAYS`
- `PASS_WARN_AGE`

For password quality, consider PAM modules such as `libpam-pwquality` and the `pwquality` configuration.

Check account expiration and password aging with:

`chage -l <username>`

For user encryption, `ecryptfs-utils` can be used on systems that support it.