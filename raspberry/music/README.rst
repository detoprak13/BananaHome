mps
===

.. image:: http://badge.fury.io/py/mps.svg
    :target: https://pypi.python.org/pypi/mps
.. image:: https://img.shields.io/pypi/dm/mps.svg
    :target: https://pypi.python.org/pypi/mps
.. image:: https://img.shields.io/pypi/wheel/mps.svg
    :target: http://pythonwheels.com/
    :alt: Wheel Status


Features
--------
- Search and stream music
- Search albums or single tracks
- Create playlists
- Download tracks
- Works with Python 2.7+ and 3.3+
- Works with Windows, Linux and Mac OS X 
- No Python dependencies
- Requires mplayer

Screenshots
-----------

Search
~~~~~~

.. image:: http://np1.github.io/mps-images/search.png

Playback
~~~~~~~~

.. image:: http://np1.github.io/mps-images/playback.png

Album Tracks Search
~~~~~~~~~~~~~~~~~~~

.. image:: http://np1.github.io/mps-images/album-search.png
.. image:: http://np1.github.io/mps-images/album-match.png

Playlists
~~~~~~~~~

.. image:: http://np1.github.io/mps-images/playlists.png



Installation
------------

Using `pip <http://www.pip-installer.org>`_::
    
    [sudo] pip install mps

Using `git <http://www.git-scm.com>`_::

    git clone https://github.com/np1/mps.git
    cd mps
    python setup.py install
   
Manually:

  Download `zip <https://github.com/np1/mps/archive/master.zip>`_ or `tar.gz <https://github.com/np1/mps/archive/master.tar.gz>`_ and extract

  From within the mps directory::

    python setup.py install


Mac OS X installation notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
Install mplayer with `MacPorts <http://www.macports.org>`_::

    sudo port install MPlayer


Windows installation notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the python `colorama <https://pypi.python.org/pypi/colorama>`_ module to get colors (optional)::

    pip install colorama

Download mplayer for your CPU type from the "Build Selection table" `here
<http://oss.netfarm.it/mplayer-win32.php>`_. 

Extract the mplayer.exe file, saving it to your mps directory or a PATH
directory


Upgrading
---------

It is recommended you update to the latest version.

Upgrade pip installation::

    sudo pip install mps --upgrade

Upgrade git clone::

    (from within the mps directory)

    git pull

Usage
-----

mps is run on the command line using the command::
    
    mps
    
Enter ``h`` from within the program for help.

Searching
~~~~~~~~~

You can enter an artist/song name to search for songs.
Track searches must be prefixed with either a . or / character.

Enter ``n`` or ``p`` to go to the next / previous page of results

To search for an album, enter ``album`` optionally followed by the album title.

When a list of songs is displayed, such as search results or a playlist, you
can use the following commands:

Downloading
~~~~~~~~~~~
``d 3`` to download song 3

Playback
~~~~~~~~

``all`` to play all displayed tracks

``1,2,3`` to play songs 1 2 and 3

``2-4,6,6-3`` to play songs 2, 3, 4, 6, 6, 5, 4, 3

Note: The commands ``shuffle`` and ``repeat`` can be inserted at the start or
end of any of the above to enable those play modes: eg, ``shuffle 1-4`` or
``2-4,1 repeat`` 

Editing
~~~~~~~
``rm 1,5`` to remove songs 1 and 5.

``rm 1,2,5-7`` to remove songs 1,2 and 5-7.

``rm all`` to remove all songs

``sw 1,3`` to swap the position of songs 1 and 3

``mv 1,3`` to move song 1 to postion 3

Playlist commands
~~~~~~~~~~~~~~~~~

``add 1,2,3`` to add songs 1,2 and 3 to the current playlist. 

``add 1-4,6,8-10`` to add songs 1-4, 6, and 8-10 to the current playlist
    
``add 1-4,7 <playlist_name>`` to add songs 1-4 and 7 to a saved playlist.  A
new playlist will be created if the given name doesn't already exist.

``vp`` to view the current playlist (then use rm, mv and sw to modify it)

``ls`` to list your saved playlists

``open <playlist_name or ID>`` to open a saved playlist as the current playlist 

``view <playlist_name or ID>`` to view a playlist (leaves current playlist intact)

``play <playlist_name or ID>`` to play a saved playlist directly.

``save`` or ``save <playlist_name>`` to save the currently displayed songs as a
stored playlist on disk

``rmp <playlist_name or ID>`` to delete a playlist from disk

``mv <old_name or ID> <new_name>`` to rename a playlist

``q`` to quit

``h`` for help

Other Commands
--------------

``top`` show top tracks this week

``top3m`` show top tracks for last 3 months

``top6m`` show top tracks for last 6 months

``topyear`` show top tracks for last year

``topall`` show all time top tracks

``list [pleer playlist url]``` to import a playlist from the web.

Advanced Tips
-------------

Playlist Name Completion
~~~~~~~~~~~~~~~~~~~~~~~~

When using ``open``, ``view`` or ``play``  to access a playlist, you can enter
the first few characters instead of the whole name.  The first alphabetically
matching playlist will be opened / displayed.

Invocation
~~~~~~~~~~

To play a saved playlist when invoking mps use the following command:

    ``mps play <playlistname>``

This also works for other commands, eg:

    ``mps .mozart`` to search 

    ``mps view <playlistname>`` to view a saved playlist

    ``mps ls`` to list saved playlists

    ``mps top`` to list top tracks this week

    ``mps open moz`` to open a saved playlist called mozart.

Specifying Ranges
~~~~~~~~~~~~~~~~~

When selecting songs for playback, removing or adding you can use ``5-`` to 
select song 5 upward and ``-5`` to select up to song 5.  This can be included
with other choices so for example: ``5,3,7-,-2``.  You can also use spaces
instead of commas eg. ``5 3 7- -2``.

Quality / Bitrate
~~~~~~~~~~~~~~~~~

Add ``+best`` to a search query to return high bitrate results or ``+good`` to
exclude them.

Using MPV instead of MPlayer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have `mpv <http://mpv.io>`_ installed and want to use that instead of mplayer;

From within mps::

    set player mpv
    set playerargs --really-quiet --no-video

Other Configuration
~~~~~~~~~~~~~~~~~~~

To view configuration, enter ``set`` and to change any item enter: 
``set <item> <value>``.  This can be used to change the download path (DDIR)
and will persist after exiting the program.  To reset all settings to default,
use ``set all default`` or for a single item, ``set <item> default``

Disclaimer
~~~~~~~~~~

Use this software at your own risk, it downloads content from pleer.com, an
online mp3 file repository.
