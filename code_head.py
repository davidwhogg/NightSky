#!/usr/bin/env python
#-*- coding: utf-8 -*-
##############################################################################
# THIS CODE COMES WITH NO WARRANTY; USE AT YOUR OWN RISK!
##############################################################################
# name:
#   nightsky
# purpose:
#   interactively plot the celestial sphere
# to-do items:
#   - how to do the Moon and Earth relative to EMB?
#   - how to do the Observatory relative to the EMB?
#   - document each step very clearly
#   - ought to include the ecliptic in the RA,Dec grid
# comments:
#   Because there are no proper motions and only simple orbital element time
#     derivatives, this code cannot be used to predict the far future or far
#     past (ie, it will only be accurate for the next and past 50 years or so).
#     If you want to do far-future or far-past stuff you need to add:
#     - star proper motions where known (some are in the Bright Star Catalog)
#     - a dynamical model of Solar System evolution
#     - a *very good* dynamical model of the Earth-Moon system with
#       perturbations
#   In principle, the epoch of the coordinate system (RA, Dec), the planet
#     ephemerides, and the ecliptic must be synchronized.  Right now they are
#     all fixed at J200.0 with no capability for changing; this needs to be
#     reconsidered in, say 50 years.  If you want to update the epoch (to, say
#     2050), you will have to replace, at least:
#     - the Bright Star Catalog written in the huge literal
#     - the ecliptic angle defined as the global EclipticAngle
#     - the planet data in PlanetCatalog()
# bugs:
#   - way too many modify_font() calls; can't widgets inherit the font of
#     their parent and then all these font calls could be replaced with one?
#   - some fonts are different in hyphen and minus sign.  When one of these
#     fonts is in use (you will see short minus signs), replace '-' with
#     '\u2212'.
#   - ra,dec and stars buttons ought to be toggles.
#   - super-slow when the celestial coordinate grid is turned on.
#   - the planets don't change brightness with phase / elongation
#   - the observer is at the Earth-Moon barycenter, not the observatory
#   - probably fails when (alt,az)=NCP
#   - probably fails when alt=90
#   - LST calculation approximate; in particular it doesn't use the "equation
#     of the equinoxes; this should only matter at the seconds level of
#     accuracy
#   - Technically, sunset is defined to be the moment when the limb of the Sun
#     just becomes invisible, which, because of the finite size of the Sun
#     (16 arcmin) and atmospheric refraction (34 arcmin), is when the center
#     of the Sun is 50 arcmin below the unrefracted horizon.  Right now, the
#     Sun disappears from view in the code when it's center hits the horizon,
#     although the "day" indicator switches to "twilight" at 50 arcmin below
#     the horizon.
# dependencies:
#   - sys ?
#   - gettext # for language translation
#   - math
#   - datetime # for UTC and time difference operations
#   - string # for processing text input
#   - pygtk & gtk
# author:
#   David W. Hogg (New York University) http://cosmo.nyu.edu/hogg/
#   - Hogg gratefully acknowledges help from Keir Mierle (U of Toronto).
#   - Please send comments, bug reports, bug fixes, and code enhancements
#     to Hogg at the email address available at <http://cosmo.nyu.edu/hogg/>.
# license:
#   copyright David W. Hogg 2007, all rights reserved
#   Eventually I will licence this with some open-source license, but I haven't
#     figured out which one yet.
# revision history:
#   2007-01-19  converted Hogg legacy code into a GTK program - Hogg
#   2007-01-24  basically works - Hogg
###############################################################################

import sys
import gettext
import math
import datetime
import string
import pygtk; pygtk.require("2.0")
import gtk
import pango

# translation tool
_= gettext.gettext

# The next MANY lines include the Bright Star Catalog as a python literal.
# The proper python code starts below the literal.
# START bright star catalog literal
