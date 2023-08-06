### Table of contents 

1. [About](#About)
2. [Screenshots](#Screenshots)
3. [Installation](#Installation)
4. [Requirements](#Requirements)
5. [Recommended](#Recommended)
6. [Testing](#Testing)
7. [Command Line Tool Usage](#Command-Line-Tool-Usage)
8. [How to start](#How-to-start)
9. [Configuration files](#Configuration-files)
10. [Repositories](#Repositories)
11. [Multilib Packages](#Multilib-Packages)
12. [Issues](#Issues)
13. [Donate](#Donate)
14. [Support](#Support)
15. [Copyright](#Copyright)

<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_install_packages.png" width="400" height="200">
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/poweredbyslack.gif" width="200" height="50">


### About

Slpkg is a software package manager that installs, updates and removes packages on [Slackware](https://www.slackware.com)-based systems.
It automatically calculates dependencies and figures out what things need to happen to install packages.
Slpkg makes it easier to manage groups of machines without the need for manual updates.
Slpkg works in accordance with the standards of the [slackbuilds.org](https://www.slackbuilds.org) organization to build packages.
It also uses the Slackware Linux instructions for installing, upgrading or removing packages.

### Screenshots

```
$ slpkg repo-info
```
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_repo_info.png" width="900">

```
$ slpkg install audacity --repository=alien
```
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_install.png" width="900">
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_install_done.png" width="900">

```
$ slpkg remove audacity
```
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_remove.png" width="900">
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_remove_done.png" width="900">

```
$ slpkg dependees --pkg-version --full-reverse greenlet
```
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_dependees.png" width="900">

```
$ slpkg tracking --pkg-version Flask awscli pychess
```
<img src="https://gitlab.com/dslackw/images/raw/master/slpkg/slpkg_tracking.png" width="900">

### Installation

```
$ tar xvf slpkg-4.8.3.tar.gz
$ cd slpkg-4.8.3
$ ./install.sh
```

### Requirements

```
SQLAlchemy >= 1.4.46
python3-pythondialog >= 3.5.3
python3-progress >= 1.6
```

### Recommended

Stay always updated, see my other project SUN [(Slackware Update Notifier)](https://gitlab.com/dslackw/sun)


### Testing

The majority of trials have been made in Slackware x86_64 'stable' environment.


### Command Line Tool Usage

```
slpkg - version 4.8.3

USAGE:
  slpkg [COMMAND] [OPTIONS] [FILELIST|PACKAGES...]

DESCRIPTION:
  Package manager utility for Slackware.

COMMANDS:
  -u, update                    Update the package lists.
  -U, upgrade                   Upgrade all the packages.
  -c, check-updates             Check for news on ChangeLog.txt.
  -I, repo-info                 Prints the repositories information.
  -g, configs                   Edit the configuration file.
  -L, clean-logs                Clean dependencies log tracking.
  -T, clean-data                Clean all the repositories data.
  -D, clean-tmp                 Delete all the downloaded sources.
  -b, build [packages...]       Build only the packages.
  -i, install [packages...]     Build and install the packages.
  -R, remove [packages...]      Remove installed packages.
  -d, download [packages...]    Download only the scripts and sources.
  -f, find [packages...]        Find installed packages.
  -w, view [packages...]        View packages from the repository.
  -s, search [packages...]      Search packages from the repository.
  -e, dependees [packages...]   Show which packages depend on.
  -t, tracking [packages...]    Tracking the packages dependencies.

OPTIONS:
  -y, --yes                     Answer Yes to all questions.
  -j, --jobs                    Set it for multicore systems.
  -O, --resolve-off             Turns off dependency resolving.
  -r, --reinstall               Upgrade packages of the same version.
  -k, --skip-installed          Skip installed packages.
  -a, --install-data            Install data into the database only.
  -E, --full-reverse            Full reverse dependency.
  -S, --search                  Search packages from the repository.
  -n, --no-silent               Disable silent mode.
  -p, --pkg-version             Print the repository package version.
  -P, --parallel                Download files in parallel.
  -o, --repository=NAME         Change repository you want to work.
  -z, --directory=PATH          Download files to a specific path.

  -h, --help                    Show this message and exit.
  -v, --version                 Print version and exit.
```


### How to start

If you are going to use only the [SlackBuilds.org](https://slackbuilds.org) repository, you don't need to edit
the `/etc/slpkg/repositories.toml` file, otherwise edit the file and set `true` the repositories you want.

The second step is to update the package lists and install the data to the database, just run:


```
    $ slpkg update
```

Now you are ready to start!

To install a package, run:

```
    $ slpkg install <package_name>
```

or change the repository:

```
    $ slpkg install <package_name> --repository=<repo_name>
```

You can install a whole repository with the command:

```
    $ slpkg install '*' --repository=<repository_name>
```

To remove a package with the dependencies:

```
    $ slpkg remove <package_name>
```

If you want to search a package from all repositories, run:

```
    $ slpkg search <package_name> --repository='*'
```

Edit the configuration `/etc/slpkg/slpkg.toml` file:

```
    $ slpkg configs
```

For further information, please read the manpage:

```
    $ man slpkg
```


### Configuration files

```
/etc/slpkg/slpkg.toml
    General configuration of slpkg
    
/etc/slpkg/repositories.toml
    Repositories configuration

/etc/slpkg/blacklist.toml
    Blacklist of packages
```

### Repositories

This is the list of the supported repositories:

* [Slackbuilds](https://slackbuilds.org/)
* [Ponce](https://cgit.ponce.cc/slackbuilds/)
* [Slackware](https://slackware.uk/slackware/slackware64-15.0/)
* [Slackware Extra](https://slackware.uk/slackware/slackware64-15.0/extra/)
* [Slackware Patches](https://slackware.uk/slackware/slackware64-15.0/patches/)
* [Alien](http://slackware.uk/people/alien/sbrepos/15.0/x86_64/)
* [Multilib](https://slackware.nl/people/alien/multilib/15.0/)
* [Restricted](https://slackware.nl/people/alien/restricted_sbrepos/15.0/x86_64/)
* [Gnome](https://reddoglinux.ddns.net/linux/gnome/41.x/x86_64/)
* [Msb](https://slackware.uk/msb/15.0/1.26/x86_64/)
* [Csb](https://slackware.uk/csb/15.0/x86_64/)
* [Conraid](https://slack.conraid.net/repository/slackware64-current/)
* [Slackonly](https://packages.slackonly.com/pub/packages/15.0-x86_64/)
* [SalixOS](https://download.salixos.org/x86_64/slackware-15.0/)
* [SalixOS Extra](https://download.salixos.org/x86_64/slackware-15.0/extra/)
* [SalixOS Patches](https://download.salixos.org/x86_64/slackware-15.0/patches/)
* [Slackel](http://www.slackel.gr/repo/x86_64/current/)
* [Slint](https://slackware.uk/slint/x86_64/slint-15.0/)


### Multilib Packages

Slackware for x86_64 - multilib packages & install instructions:

Please read the file [README](https://gitlab.com/dslackw/slpkg/-/raw/master/filelists/multilib/README) you will find in the folder [multlib](https://gitlab.com/dslackw/slpkg/-/tree/master/filelists/multilib)


### Issues

Please report any bugs in [ISSUES](https://gitlab.com/dslackw/slpkg/issues)

Note: With the issue, please reference the log file you will find in the /tmp/slpkg/logs/slpkg.log path and paste it too.


### Donate

If you feel satisfied with this project and want to thank me, treat me to a coffee ☕ !

[<img src="https://gitlab.com/dslackw/images/raw/master/donate/paypaldonate.png">](https://www.paypal.me/dslackw)


### Support

Please support:

* [Slackware](https://www.patreon.com/slackwarelinux) project.
* [SlackBuilds](https://slackbuilds.org/contributors/) repository.
* [AlienBob](https://alien.slackbook.org/blog/) Eric Hameleers.

Thank you all for your support!


### Copyright

Copyright 2014-2023 © Dimitris Zlatanidis.
Slackware® is a Registered Trademark of Patrick Volkerding.
Linux is a Registered Trademark of Linus Torvalds.
