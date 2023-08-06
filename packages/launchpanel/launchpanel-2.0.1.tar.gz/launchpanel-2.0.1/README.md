
# Overview


LaunchPanel is a simple interface designed to expose LaunchPad Actions
to the user in an intuitive way.

LaunchActions are displayed in icon-centric list widgets, and they are
organised into tabs based on their groups. The user has the ability to
define tab orientation, icon size and plugin locations.

Video demo coming soon...


# Installation

If you use pip, you can simply run ```pip install launchpanel```. That will 
pull down the required dependencies (qute, scribble & factories) automatically.

Alternatively, if you just want to download a file and extract everything to a 
location you can download __packaged_launchpanel.zip__ and extract the contents
of that zip to somewhere where your python interpreter/application is looking
for python modules.

If you want to look at some example plugins - some of which use simple static
data in their plugin whilst others dynamically generate plugins at runtime, you
can pull down the __example_plugins__ folder.

# Running

You can run launchpanel by calling:

```python
import launchpanel
launchpanel.launch()
```

This code will work in both standalone python as well as supported applications
such as Max, Maya and Motion Builder (see details of qute for full list of
application support https://github.com/mikemalinowski/qute)

If you want to easily run Launch Panel in standalone for everyday use on
windows the easiest thing to do is to create a .cmd file on your desktop with
the following in it: 

```call c:\python27\pythonw.exe /my/path/to/launchpand/run.py```


# Environments


If you're using launchpanel in multiple contexts it can be useful to
differentiate one from the other. This can be done by setting the
environment_id.

This is simply a string identifier which defines where it will store its
settings/preferences.

```python
import launchpanel
launchpanel.launch(environment_id='foo')
```

The above instance will not cross over with the instance created below, meaning
each can have their own paths to look for actions.

```python
import launchpanel
launchpanel.launch(environment_id='bar')
```

This is particulary useful if you are running multiple projects and want a
bespoke set of plugins displayed for each one.


## Dependencies


This module has the following dependencies:

    * launchpad
    * qute
    * scribble (pip install scribble)


# Credits & Collaboration

This module was inspired by some excellent collaborative projects with a 
fantastic tech-artist called __Toby Harrison-Banfield__.

I am always open to collaboration, so if you spot bugs lets me know, or if
you would like to contribute or get involved just shout!


# Compatibility

Launchpad has been tested under Python 2.7 and Python 3.7 on Windows and Ubuntu.
