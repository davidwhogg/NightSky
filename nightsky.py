# END bright star catalog literal
# whew !

piover180= math.pi/180.0
piunder180= 180.0/math.pi

def VersionString():
    return "alpha test version"

# class for handling all simple 3-d vector operations
class Vector:
    def __init__(self,start):
        self.data= start
    def __neg__(self):
        return Vector([-self.data[0],-self.data[1],-self.data[2]])
    def __add__(self,other):
        return Vector([self.data[0]+other.data[0],
                       self.data[1]+other.data[1],
                       self.data[2]+other.data[2]])
    def __sub__(self,other):
        return Vector([self.data[0]-other.data[0],
                       self.data[1]-other.data[1],
                       self.data[2]-other.data[2]])
    def __getitem__(self,index):
        return self.data[index]
    def scale(self,scalar):
        return Vector([scalar*self.data[0],
                       scalar*self.data[1],
                       scalar*self.data[2]])
    def norm(self):
        return math.sqrt(self.data[0]*self.data[0]+
                         self.data[1]*self.data[1]+
                         self.data[2]*self.data[2])
    def hat(self):
        return self.scale(1.0/self.norm())
    def dot(self,other):
        return (self.data[0]*other.data[0]+
                self.data[1]*other.data[1]+
                self.data[2]*other.data[2])
    def cross(self,other):
        return Vector([self.data[1]*other.data[2]
                      -self.data[2]*other.data[1],
                       self.data[2]*other.data[0]
                      -self.data[0]*other.data[2],
                       self.data[0]*other.data[1]
                      -self.data[1]*other.data[0]])

# define crucial unit vectors
ehat= [Vector([1.0,0.0,0.0]),
       Vector([0.0,1.0,0.0]),
       Vector([0.0,0.0,1.0])]
Equinox= ehat[0]
CelestialPole= ehat[2]
EclipticAngle= 23.43928*piover180 # radians
EclipticPole= (ehat[2].scale(math.cos(EclipticAngle))
              -ehat[1].scale(math.sin(EclipticAngle)))

# convert RA, Dec pair (in deg) to a three-vector
def RaDecToVector(aa,dd):
    arad= aa*piover180
    drad= dd*piover180
    return (
        ehat[0].scale(math.cos(drad)*math.cos(arad))
       +ehat[1].scale(math.cos(drad)*math.sin(arad))
       +ehat[2].scale(math.sin(drad)))

# convert alt, az pair (in deg) plus zenith direction to a three-vector
#      probably fails when (alt,az)=NCP
def AltAzToVector(alt,az,zz):
    altrad= alt*piover180
    azrad= az*piover180
    ee, nn= Normals(zz,ehat[2])
    return (
        nn.scale(math.cos(altrad)*math.cos(azrad))
       +ee.scale(math.cos(altrad)*math.sin(azrad))
       +zz.scale(math.sin(altrad)))

# make orthogonal normals to an input three-vector
def Normals(rr,zz=None):
    if (zz == None):
        zz= ehat[2]
        if (math.fabs(rr.data[1]) < math.fabs(rr.data[2])): zz= ehat[1]
        if ((math.fabs(rr.data[0]) < math.fabs(rr.data[2])) and
            (math.fabs(rr.data[0]) < math.fabs(rr.data[1]))): zz= ehat[0]
    zz= zz.hat()
    rhat= rr.hat()
    vv= zz-rhat.scale(zz.dot(rhat))
    vv= vv.hat()
    uu= vv.cross(rhat)
    return uu,vv

# make a small circle on the sphere
#     name   - name to give to "stars" that make up the circle
#     rr     - center of polygon
#     delta  - angular radius (rad)
#     nn     - number of sides
#     half   - set to true if you want only the first half of the circle
def Polygon(name,rr,delta,nn):
    uu, vv= Normals(rr)
    maxtheta= 2.0*math.pi
    ww= []
    ii= 0L
    while (ii <= nn):
        theta= maxtheta*ii/nn
        wwii= Star(name,None,None,None)
        wwii.SetVector3(uu.scale(math.sin(delta)*math.cos(theta))
                        +vv.scale(math.sin(delta)*math.sin(theta))
                        +rr.scale(math.cos(delta)))
        ww.append(wwii)
        ii= ii+1
    return ww

# class for objects that are like stars, ie objects that have a fixed
#     position on the celestial sphere.  You can either initialize them with
#     an RA, Dec, or else input None for RA and Dec and subsequently set
#     a 3-vector position with the function SetVector3().
class Star:
    def __init__(self,name,ra,dec,Vmag):
        self.Name= name
        self.RA= ra
        self.Dec= dec
        self.Vmag= Vmag
        if ((ra != None) and (dec != None)):
            self.SetVector3(RaDecToVector(ra,dec))
        else: self.Vector3= None
        self.Vector2= None
        self.DrawLabelEvenIfFaint= False
    def SetVector3(self,vector3):
        self.Vector3= vector3
        return True
    def SetVector2(self,vector2):
        self.Vector2= vector2
        return True

# class for objects that are like planets, ie, objects with orbits around
#     the Sun.
#     name:        planet name, of course
#     elements:    (a_AU, e, I_deg, L_deg, omega_deg, Omega_deg) at epoch
#     elementsdot: time derivative of elements per century at epoch
#     epoch:       datetime UTC of epoch
class Planet:
    def __init__(self,name,elements,elementsdot,epoch,Vmag):
        self.Name= name
        self.ElementsAtEpoch= elements
        self.ElementDerivatives= elementsdot
        self.Epoch= epoch
        self.Vmag= Vmag
        self.ElementNames= ["a","e","I","L","omega","Omega"]
        self.ElementUnits= ["AU","","deg","deg","deg","deg"]
        self.Vector2= None
        self.DrawLabelEvenIfFaint= True
    def Elements(self,UTC):
        deltat= UTC-self.Epoch
        deltaday= deltat.days+deltat.seconds/86400.0
        deltacentury= deltaday/36525.0
        elements= []
        ii= 0
        for element in self.ElementsAtEpoch:
            thiselement= (self.ElementsAtEpoch[ii]
                          +self.ElementDerivatives[ii]*deltacentury)
            if (self.ElementUnits[ii] == "deg"):
                while (thiselement > 180.0): thiselement-= 360.0
                while (thiselement < -180.0): thiselement+= 360.0
            elements.append(thiselement)
            ii+= 1
        return elements
    def Vector3(self,UTC):
        vector3= Vector((0,0,0))
        if (self.ElementsAtEpoch[0] > 0):
            elements= self.Elements(UTC)
            semimajoraxis= elements[0]
            eccentricity= elements[1]
            inclination= elements[2]*piover180 # radians
            meananomaly= (elements[3]-elements[4])*piover180 # radians
            while (meananomaly > math.pi): meananomaly-= 2.0*math.pi
            while (meananomaly <= -math.pi): meananomaly+= 2.0*math.pi
            argumentperihelion= (elements[4]-elements[5])*piover180 # rad
            longascendingnode= elements[5]*piover180 # radians
            tmpydir= EclipticPole.cross(Equinox)
            ascendingnode= (Equinox.scale(math.cos(longascendingnode))
                            +tmpydir.scale(math.sin(longascendingnode)))
            tmpydir= EclipticPole.cross(ascendingnode)
            orbitpole= (EclipticPole.scale(math.cos(inclination))
                        -tmpydir.scale(math.sin(inclination)))
            tmpydir= orbitpole.cross(ascendingnode)
            periheliondir= (ascendingnode.scale(math.cos(argumentperihelion))
                            +tmpydir.scale(math.sin(argumentperihelion)))
            tmpydir= orbitpole.cross(periheliondir)
            eccentricanomaly= meananomaly+eccentricity*math.sin(meananomaly)
            deltae= 100.0
            while (deltae > 1e-6):
                newmeananomaly= (eccentricanomaly
                                 -eccentricity*math.sin(eccentricanomaly))
                deltam= meananomaly-newmeananomaly
                deltae= deltam/(1.0-eccentricity*math.cos(eccentricanomaly))
                eccentricanomaly+= deltae
            xx= semimajoraxis*(math.cos(eccentricanomaly)-eccentricity)
            yy= semimajoraxis*(math.sqrt(1-eccentricity*eccentricity)
                               *math.sin(eccentricanomaly))
            vector3= periheliondir.scale(xx)+tmpydir.scale(yy)
        return vector3
    def SetVector2(self,vector2):
        self.Vector2= vector2
        return True

# make list of planets
def PlanetCatalog():
    # UTC for 2000 January 1.5
    j2000= datetime.datetime(2000,1,1,12,0,0,0,tzinfo=None)
    planets= []
    planet= Planet(_('Sun'),(0,0,0,0,0,0),(0,0,0,0,0,0),j2000,-26.8)
    planets.append(planet)
    planet= Planet(_('Mercury'),
                   (  0.38709927, 0.20563593, 7.00497902,
                       252.25032350, 77.45779628, 48.33076593),
                   (  0.00000037, 0.00001906,-0.00594749,
                    149472.67411175, 0.16047689,-0.12534081),j2000,0.0)
    planets.append(planet)
    planet= Planet(_('Venus'),
                   (    0.72333566, 0.00677672, 3.39467605,
                       181.97909950,131.60246718, 76.67984255),
                   (  0.00000390,-0.00004107,-0.00078890,
                     58517.81538729, 0.00268329,-0.27769418),j2000,-4.0)
    planets.append(planet)
    planet= Planet(_('Earth-Moon barycenter'),
                   (    1.00000261, 0.01671123,-0.00001531,
                       100.46457166,102.93768193,  0.0),
                   (  0.00000562,-0.00004392,-0.01294668,
                     35999.37244981, 0.32327364, 0.0),j2000,None)
    planets.append(planet)
    planet= Planet(_('Mars'),
                   (     1.52371034, 0.09339410, 1.84969142,
                        -4.55343205,-23.94362959, 49.55953891),
                   (  0.00001847, 0.00007882,-0.00813131,
                     19140.30268499, 0.44441088,-0.29257343),j2000,1.0)
    planets.append(planet)
    planet= Planet(_('Jupiter'),
                   (  5.20288700, 0.04838624, 1.30439695,
                        34.39644051, 14.72847983,100.47390909),
                   ( -0.00011607,-0.00013253,-0.00183714,
                      3034.74612775, 0.21252668, 0.20469106),j2000,-2.0)
    planets.append(planet)
    planet= Planet(_('Saturn'),
                   (   9.53667594, 0.05386179, 2.48599187,
                        49.95424423, 92.59887831,113.66242448),
                   ( -0.00125060,-0.00050991, 0.00193609,
                      1222.49362201,-0.41897216,-0.28867794),j2000,0.0)
    planets.append(planet)
#    planet= Planet(_('Uranus'),
#                   (  19.18916464, 0.04725744, 0.77263783,
#                       313.23810451,170.95427630, 74.01692503),
#                   ( -0.00196176,-0.00004397,-0.00242939,
#                       428.48202785, 0.40805281, 0.04240589),j2000,+6.0)
#    planets.append(planet)
#    planet= Planet(_('Neptune'),
#                   ( 30.06992276, 0.00859048, 1.77004347,
#                       -55.12002969, 44.96476227,131.78422574),
#                   (  0.00026291, 0.00005105, 0.00035372,
#                       218.45945325,-0.32241464,-0.00508664),j2000,+8.0)
#    planets.append(planet)
#    planet= Planet(_('Pluto'),
#                   (   39.48211675, 0.24882730,17.14001206,
#                       238.92903833,224.06891629,110.30393684),
#                   ( -0.00031596, 0.00005170, 0.00004818,
#                       145.20780515,-0.04062942,-0.01183482),j2000,+14.0)
#    planets.append(planet)
    return planets

# make grid for celestial coordinates; ie, make RA, Dec grid
def CelestialGrid():
    nside= 90
    grid= []
    labels= []
    ra= 0.0
    while (ra < 179):
        name= "%02.0f<sup>h</sup>" % (ra/15.0) # hours
        ra2= ra+180.0
        name2= "%02.0f<sup>h</sup>" % (ra2/15.0) # hours
        pole= RaDecToVector(ra+90,0.0)
        line= Polygon(name,pole,0.5*math.pi,nside)
        grid+= line
        dec= -90.0+22.5
        while (dec < 89):
            labels.append(Star(name,ra,dec,None))
            labels.append(Star(name2,ra2,dec,None))
            dec += 45.0
        ra+= 30.0
    dec= -60.0
    while (dec < 89):
        name= ur"%+02.0f\u00B0" % dec # deg
        nside2= int(nside*math.cos(dec*piover180)+0.5)
        line= Polygon(name,CelestialPole,(90.0-dec)*piover180,nside2)
        grid+= line
        ra= 15.0
        while (ra < 359):
            labels.append(Star(name,ra,dec,None))
            ra+= 60.0
        dec+= 30.0
    ra= 45.0
    while (ra < 359):
        labels.append(Star(_('celestial equator'),ra,0.0,None))
        ra+= 60.0
    return grid,labels

# make ecliptic line and labels
def SolarSystemGrid():
    nside= 90
    grid= []
    labels= []
    name= _('ecliptic')
    line= Polygon(name,EclipticPole,0.5*math.pi,nside)
    grid+= line
    ra= 50.0 # deg
    while (ra < 359):
        label= Star(name,None,None,None)
        vec= EclipticPole.cross(RaDecToVector(ra,0.0)).hat()
        label.SetVector3(vec)
        labels.append(label)
        ra+= 60.0
    return grid,labels

# make horizon line
def LocalGrid(zenith):
    nside= 90
    epsilon= 0.0001
    grid= []
    labels= []
    name= _('horizon')
    line= Polygon(name,zenith,0.5*math.pi,nside)
    grid+= line
    az= 22.5 # deg
    while (az < 359):
        label= Star(name,None,None,None)
        label.SetVector3(AltAzToVector(epsilon,az,zenith))
        labels.append(label)
        az+= 45.0
    return grid,labels

# make list of labels for celestial (fixed) sky points
def CelestialLabelCatalog():
    labels= []
    vv= Star(_('North Pole'),None,None,None)
    vv.SetVector3(RaDecToVector(0.0,90.0))
    labels.append(vv)
    vv= Star(_('South Pole'),None,None,None)
    vv.SetVector3(RaDecToVector(0.0,-90.0))
    labels.append(vv)
    return labels

# make list of labels for local (position-dependent) sky points:
def LocalLabelCatalog(ObsCon):
    epsilon= 0.0001
    labels= []
    vv= Star(_('zenith'),None,None,None)
    vv.SetVector3(ObsCon.Zenith())
    labels.append(vv)
    vv= Star(_('nadir'),None,None,None)
    vv.SetVector3(ObsCon.Zenith().scale(-1.0))
    labels.append(vv)
    vv= Star(_('N'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,0.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('NE'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,45.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('E'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,90.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('SE'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,135.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('S'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,180.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('SW'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,225.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('W'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,270.0,ObsCon.Zenith()))
    labels.append(vv)
    vv= Star(_('NW'),None,None,None)
    vv.SetVector3(AltAzToVector(epsilon,315.0,ObsCon.Zenith()))
    labels.append(vv)
    return labels

# project from 3D to 2D plotting plane
#     vv is a 3-vector
#     pp is the point of view position
#     phat is the unit vector for pp
#     XX,YY are normals to pp
#     zoom,width,height are related to going to pixels
#     note that the y-direction is screwy
#     qq.dot(pp) condition means the star can be seen from this viewpoint
#     qq.dot(vv) condition means the star is on the *inside* of the celestial
#         sphere
def ProjectVector(vv,pp,phat,pminusphat,pdotp,XX,YY,zoom,width,height):
    buffer= 50 # pix
    qq= vv+pminusphat
    vv2= None
    qdotp= qq.dot(pp)
    if ((qdotp > 0.0) and (qq.dot(vv) > 0.0)):
        RR= qq.scale(pdotp/qdotp)-pp
        xx= RR.dot(XX)*zoom+width/2.0
        if ((xx > (-buffer)) and (xx < (width+buffer))):
            yy= height/2.0-RR.dot(YY)*zoom
            if ((yy > (-buffer)) and (yy < (height+buffer))):
                vv2= [xx,yy]
    return vv2

# The ObservingContext class contains everything you need to know about:
#     where you are standing
#     when you are observing
#     where you are looking
#     what you can see
class ObservingContext:
    def __init__(self):
        self.DefaultLatitude= 40.76 # deg
        self.SetLatitude(self.DefaultLatitude)
        self.DefaultEastLongitude= -73.92 # deg E of N
        self.SetEastLongitude(self.DefaultEastLongitude)
        self.DefaultAlt= 30.0
        self.SetAlt(self.DefaultAlt) # deg
        self.SetAz(0.0) # deg
        self.ViewDistance= 1.5
        self.Faintest= 4.0 # V mag
        self.Zoom= 500
        self.DrawStarLabels= False
        self.DrawCelestialGrid= False
        self.DrawSolarSystemGrid= False
        self.DrawHorizon= True
        self.ClipHorizon= True
        self.ReverseVideo= False
        self.DaylightString= None
        self.ResetUTC()
    def SetLatitude(self,latitude):
        if (latitude > 90.0): latitude= 90.0
        if (latitude < -90.0): latitude= -90.0
        self.Latitude= latitude
        return True
    def SetEastLongitude(self,longitude):
        while (longitude > 180.0): longitude= longitude-360.0
        while (longitude < -180.0): longitude= longitude+360.0
        self.EastLongitude= longitude
        return True
    def SetAlt(self,alt):
        if (alt > 89.9): alt= 89.9
        if (alt < 0.0): alt= 0.0
        self.Alt= alt
        return True
    def SetAz(self,az):
        while (az >= 360.0): az= az-360.0
        while (az < 0.0): az= az+360.0
        self.Az= az
        return True
    def SetUTC(self,UTC):
        self.UTC= UTC.replace(microsecond=0)
        return True
    def ResetUTC(self):
        self.SetUTC(datetime.datetime.utcnow())
        return True
    def SetDrawStarLabels(self,bit):
        self.DrawStarLabels= bit
        if (self.DrawStarLabels): print _('turning on star labels')
        else: print _('turning off star labels')
        return True
    def SetDrawCelestialGrid(self,bit):
        self.DrawCelestialGrid= bit
        if (self.DrawCelestialGrid): print _('turning on celestial grid')
        else: print _('turning off celestial grid')
        return True
    def SetDrawSolarSystemGrid(self,bit):
        self.DrawSolarSystemGrid= bit
        if (self.DrawSolarSystemGrid): print _('turning on ecliptic')
        else: print _('turning off ecliptic')
        return True
    def SetReverseVideo(self,bit):
        self.ReverseVideo= bit
        print _('reversing video')
        return True
    def Epoch(self):
        return datetime.datetime(2000,1,1,12,0,0,0,tzinfo=None)
    def GreenwichMeanSiderealTimeAtEpoch(self):
        return 18.697374558
    def GreenwichMeanSiderealTime(self):
        dsolartime= self.UTC-self.Epoch()
        dsolardays= (dsolartime.days
                     +dsolartime.seconds/86400.0)
        dsiderealdays= 1.002737909350795*dsolardays
        dsiderealdays= dsiderealdays-int(dsiderealdays)
        gmst= (self.GreenwichMeanSiderealTimeAtEpoch()+24.0*dsiderealdays)
        while (gmst < 0.0): gmst+= 24.0
        while (gmst >= 24.0): gmst-= 24.0
        return gmst
    def SiderealTime(self): # calculation approximate!
        LST= self.GreenwichMeanSiderealTime()+self.EastLongitude/15.0 
        while (LST < 0.0): LST= LST+24.0
        while (LST >= 24.0): LST= LST-24.0
        return LST
    def Zenith(self):
        return RaDecToVector(self.SiderealTime()*15.0,self.Latitude)
    def ViewPoint(self):
        return AltAzToVector(self.Alt,self.Az,
                             self.Zenith()).scale(self.ViewDistance)
    def LatitudeString(self):
        return "%+6.2f" % self.Latitude
    def EastLongitudeString(self):
        return "%+6.2f" % self.EastLongitude
    def InfoString(self): # html / pango markup
        lonlatstring= (ur"%s %s\u00B0%s, %s %s\u00B0%s" %
                       (_('Lat'),self.LatitudeString(),_('N'),
                        _('Lon'),self.EastLongitudeString(),_('E')))
        altazstring= (ur"%s %+3.0f\u00B0, %s %.0f\u00B0%s" %
                      (_('Alt'),self.Alt,
                       _('Az'),self.Az,_('E of N')))
        utcstring= "%s %s" % (_('UTC'),self.UTC.isoformat())
        lst= self.SiderealTime()
        lststring= ("%s %02.0f<sup>h</sup>%02.0f<sup>m</sup>" %
                    (_('LST'),int(lst),60.0*(lst-int(lst))))
        infostring= "%s / %s / %s / %s" % (lonlatstring,altazstring,
                                      utcstring,lststring)
        return infostring

class NightSky:
    def __init__(self):

# set up default astronomical information
        self.ObsCon= ObservingContext()
        self.Stars = [Star(*args) for args in LiteralBrightStarCatalog]
        self.Planets= PlanetCatalog()
        self.CelestialLabels= CelestialLabelCatalog()
        self.CelestialGrid,self.CelestialGridLabels= CelestialGrid()
        self.SolarSystemGrid,self.SolarSystemGridLabels= SolarSystemGrid()

# set up main window
        self.Window = gtk.Window()
        self.Window.set_title("NightSky: %s (%s)" % 
                              (_('the OLPC planetarium'),VersionString()))
        self.Font= pango.FontDescription("fixed")
        self.Window.connect("destroy", gtk.main_quit)
        self.BigSpacing= 8
        self.Window.set_border_width(self.BigSpacing)
        OuterBox = gtk.HBox(spacing=self.BigSpacing)
        self.Window.add(OuterBox)

# make the button box
        InnerBox= gtk.VBox(spacing=self.BigSpacing)
        OuterBox.pack_start(InnerBox,expand=False)

# make the location inputs
        SmallSpacing= 2
        LocationBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(LocationBox)
        DefaultLocationButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('default location'))
        label.modify_font(self.Font)
        DefaultLocationButton.add(label)
        LocationBox.pack_start(DefaultLocationButton)
        LatitudeEntry= gtk.Entry()
        LongitudeEntry= gtk.Entry()
        DefaultLocationButton.connect("clicked",self.ResetLocation,
                                      LatitudeEntry,LongitudeEntry)
        LatitudeBox= gtk.HBox(spacing=SmallSpacing)
        LocationBox.pack_start(LatitudeBox)
        label= gtk.Label(_('Lat'))
        label.modify_font(self.Font)
        LatitudeBox.pack_start(label)
        LatitudeBox.pack_start(LatitudeEntry)
        LatitudeEntry.connect("activate",self.ChangeLatitude,LatitudeEntry)
        LatitudeEntry.set_width_chars(7)
        LatitudeEntry.set_text(self.ObsCon.LatitudeString())
        LatitudeEntry.modify_font(self.Font)
        label= gtk.Label(ur"\u00B0%s" % _('N'))
        label.modify_font(self.Font)
        LatitudeBox.pack_start(label)
        LongitudeBox= gtk.HBox(spacing=SmallSpacing)
        LocationBox.pack_start(LongitudeBox)
        label= gtk.Label(_('Lon'))
        label.modify_font(self.Font)
        LongitudeBox.pack_start(label)
        LongitudeBox.pack_start(LongitudeEntry)
        LongitudeEntry.connect("activate",self.ChangeLongitude,LongitudeEntry)
        LongitudeEntry.set_width_chars(7)
        LongitudeEntry.set_text(self.ObsCon.EastLongitudeString())
        LongitudeEntry.modify_font(self.Font)
        label= gtk.Label(ur"\u00B0%s" % _('E'))
        label.modify_font(self.Font)
        LongitudeBox.pack_start(label)

# make the time adjustment buttons
        TimeBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(TimeBox)
        NowButton= gtk.Button()
        label= gtk.Label(_('time = now'))
        label.modify_font(self.Font)
        NowButton.add(label)
        TimeBox.pack_start(NowButton)
        NowButton.connect("clicked",self.ResetT)
        DTimeBox= gtk.HBox(spacing=SmallSpacing)
        TimeBox.pack_start(DTimeBox)
        VMinusTimeButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-1<sup>h</sup>")
        label.modify_font(self.Font)
        VMinusTimeButton.add(label)
        DTimeBox.pack_start(VMinusTimeButton)
        VMinusTimeButton.connect("clicked",self.AddDeltaT,-60*60)
        MinusTimeButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-4<sup>m</sup>")
        label.modify_font(self.Font)
        MinusTimeButton.add(label)
        DTimeBox.pack_start(MinusTimeButton)
        MinusTimeButton.connect("clicked",self.AddDeltaT,-4*60)
        PlusTimeButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+4<sup>m</sup>")
        label.modify_font(self.Font)
        PlusTimeButton.add(label)
        DTimeBox.pack_start(PlusTimeButton)
        PlusTimeButton.connect("clicked",self.AddDeltaT,4*60)
        VPlusTimeButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+1<sup>h</sup>")
        label.modify_font(self.Font)
        VPlusTimeButton.add(label)
        DTimeBox.pack_start(VPlusTimeButton)
        VPlusTimeButton.connect("clicked",self.AddDeltaT,60*60)
        DayBox= gtk.HBox(spacing=SmallSpacing)
        TimeBox.pack_start(DayBox)
        MinusSiderealDayButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-23<sup>h</sup>56<sup>m</sup>")
        label.modify_font(self.Font)
        MinusSiderealDayButton.add(label)
        DayBox.pack_start(MinusSiderealDayButton)
        MinusSiderealDayButton.connect("clicked",self.AddDeltaT,
                                            -23.9344696*60*60)
        PlusSiderealDayButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+23<sup>h</sup>56<sup>m</sup>")
        label.modify_font(self.Font)
        PlusSiderealDayButton.add(label)
        DayBox.pack_start(PlusSiderealDayButton)
        PlusSiderealDayButton.connect("clicked",self.AddDeltaT,
                                           +23.9344696*60*60)
        DayBox= gtk.HBox(spacing=SmallSpacing)
        TimeBox.pack_start(DayBox)
        MinusMonthButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-15<sup>d</sup>")
        label.modify_font(self.Font)
        MinusMonthButton.add(label)
        DayBox.pack_start(MinusMonthButton)
        MinusMonthButton.connect("clicked",self.AddDeltaT,-15*24*60*60)
        MinusDayButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-1<sup>d</sup>")
        label.modify_font(self.Font)
        MinusDayButton.add(label)
        DayBox.pack_start(MinusDayButton)
        MinusDayButton.connect("clicked",self.AddDeltaT,-24*60*60)
        PlusDayButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+1<sup>d</sup>")
        label.modify_font(self.Font)
        PlusDayButton.add(label)
        DayBox.pack_start(PlusDayButton)
        PlusDayButton.connect("clicked",self.AddDeltaT,24*60*60)
        PlusMonthButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+15<sup>d</sup>")
        label.modify_font(self.Font)
        PlusMonthButton.add(label)
        DayBox.pack_start(PlusMonthButton)
        PlusMonthButton.connect("clicked",self.AddDeltaT,15*24*60*60)
        DayBox= gtk.HBox(spacing=SmallSpacing)
        TimeBox.pack_start(DayBox)
        MinusYearButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-365<sup>d</sup>")
        label.modify_font(self.Font)
        MinusYearButton.add(label)
        DayBox.pack_start(MinusYearButton)
        MinusYearButton.connect("clicked",self.AddDeltaT,-365*24*60*60)
        PlusYearButton= gtk.Button()
        label= gtk.Label()
        label.set_markup("+365<sup>d</sup>")
        label.modify_font(self.Font)
        PlusYearButton.add(label)
        DayBox.pack_start(PlusYearButton)
        PlusYearButton.connect("clicked",self.AddDeltaT,365*24*60*60)

# make the alt buttons
        AltBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(AltBox)
        AltButtonString= ur"%s = %2.0f\u00B0" % (_('Alt'),
                                                 self.ObsCon.DefaultAlt)
        AltButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(AltButtonString)
        label.modify_font(self.Font)
        AltButton.add(label)
        AltBox.pack_start(AltButton)
        AltButton.connect("clicked",self.SetAlt,self.ObsCon.DefaultAlt)
        DAltBox= gtk.HBox(spacing=SmallSpacing)
        AltBox.pack_start(DAltBox)
        VMinusAltButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-10\u00B0")
        label.modify_font(self.Font)
        VMinusAltButton.add(label)
        DAltBox.pack_start(VMinusAltButton)
        VMinusAltButton.connect("clicked",self.AddDeltaAlt,-10.0)
        MinusAltButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-1\u00B0")
        label.modify_font(self.Font)
        MinusAltButton.add(label)
        DAltBox.pack_start(MinusAltButton)
        MinusAltButton.connect("clicked",self.AddDeltaAlt,-1.0)
        PlusAltButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"+1\u00B0")
        label.modify_font(self.Font)
        PlusAltButton.add(label)
        DAltBox.pack_start(PlusAltButton)
        PlusAltButton.connect("clicked",self.AddDeltaAlt,+1.0)
        VPlusAltButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"+10\u00B0")
        label.modify_font(self.Font)
        VPlusAltButton.add(label)
        DAltBox.pack_start(VPlusAltButton)
        VPlusAltButton.connect("clicked",self.AddDeltaAlt,+10.0)

# make the az buttons
        AzBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(AzBox)
        NESWBox= gtk.HBox(spacing=SmallSpacing)
        AzBox.pack_start(NESWBox)
        NButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('Az = N'))
        label.modify_font(self.Font)
        NButton.add(label)
        NESWBox.pack_start(NButton)
        NButton.connect("clicked",self.SetAz,0.0)
        EButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('E'))
        label.modify_font(self.Font)
        EButton.add(label)
        NESWBox.pack_start(EButton)
        EButton.connect("clicked",self.SetAz,90.0)
        SButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('S'))
        label.modify_font(self.Font)
        SButton.add(label)
        NESWBox.pack_start(SButton)
        SButton.connect("clicked",self.SetAz,180.0)
        WButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('W'))
        label.modify_font(self.Font)
        WButton.add(label)
        NESWBox.pack_start(WButton)
        WButton.connect("clicked",self.SetAz,270.0)
        DAzBox= gtk.HBox(spacing=SmallSpacing)
        AzBox.pack_start(DAzBox)
        VMinusAzButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-10\u00B0")
        label.modify_font(self.Font)
        VMinusAzButton.add(label)
        DAzBox.pack_start(VMinusAzButton)
        VMinusAzButton.connect("clicked",self.AddDeltaAz,-10.0)
        MinusAzButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"-1\u00B0")
        label.modify_font(self.Font)
        MinusAzButton.add(label)
        DAzBox.pack_start(MinusAzButton)
        MinusAzButton.connect("clicked",self.AddDeltaAz,-1.0)
        PlusAzButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"+1\u00B0")
        label.modify_font(self.Font)
        PlusAzButton.add(label)
        DAzBox.pack_start(PlusAzButton)
        PlusAzButton.connect("clicked",self.AddDeltaAz,+1.0)
        VPlusAzButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(ur"+10\u00B0")
        label.modify_font(self.Font)
        VPlusAzButton.add(label)
        DAzBox.pack_start(VPlusAzButton)
        VPlusAzButton.connect("clicked",self.AddDeltaAz,+10.0)

# make the grid and label buttons
        InfoBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(InfoBox)
        RaDecButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('RA, Dec grid'))
        label.modify_font(self.Font)
        RaDecButton.add(label)
        InfoBox.pack_start(RaDecButton)
        RaDecButton.connect("clicked",self.ToggleCelestialGrid)
        SolarButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('ecliptic'))
        label.modify_font(self.Font)
        SolarButton.add(label)
        InfoBox.pack_start(SolarButton)
        SolarButton.connect("clicked",self.ToggleSolarSystemGrid)
        StarButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('star labels'))
        label.modify_font(self.Font)
        StarButton.add(label)
        InfoBox.pack_start(StarButton)
        StarButton.connect("clicked",self.ToggleStarLabels)

# make the control box
        ControlBox= gtk.VBox(spacing=SmallSpacing)
        InnerBox.pack_start(ControlBox)
        RedrawButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('redraw'))
        label.modify_font(self.Font)
        RedrawButton.add(label)
        ControlBox.pack_start(RedrawButton)
        RedrawButton.connect("clicked",self.RedrawEvent)
        ReverseButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('reverse video'))
        label.modify_font(self.Font)
        ReverseButton.add(label)
        ControlBox.pack_start(ReverseButton)
        ReverseButton.connect("clicked",self.ToggleReverseVideo)
        QuitButton= gtk.Button()
        label= gtk.Label()
        label.set_markup(_('quit'))
        label.modify_font(self.Font)
        QuitButton.add(label)
        ControlBox.pack_start(QuitButton)
        QuitButton.connect("clicked",gtk.main_quit)

# create a big area for drawing the sky
        self.DrawingArea = gtk.DrawingArea()
        self.DrawingArea.set_size_request(900,700)
        OuterBox.pack_start(self.DrawingArea)

# standard events and the functions they spawn
        self.DrawingArea.connect("expose_event", self.ExposeEvent)
        self.DrawingArea.connect("configure_event", self.ConfigureEvent)

# show
        self.Window.show_all()

# event
    def ConfigureEvent(self, widget, event):
        width, height = self.Window.get_size()
        self.PixMap = gtk.gdk.Pixmap(widget.window,width,height)
        self.BlackGraphCon= self.DrawingArea.get_style().black_gc
        self.WhiteGraphCon= self.DrawingArea.get_style().white_gc
        self.PangoLayout= self.DrawingArea.create_pango_layout("")
        self.PangoLayout.set_font_description(self.Font)
        self.DrawEverything()
        return True

# event
    def ExposeEvent(self, widget, event):
        x, y, width, height = event.area
        self.DrawingArea.window.draw_drawable(self.BlackGraphCon,self.PixMap,
                                              0,0,0,0,width,height)
        return False

# event
    def ResetLocation(self,widget,latentry,lonentry):
        self.ObsCon.SetLatitude(self.ObsCon.DefaultLatitude)
        self.ObsCon.SetEastLongitude(self.ObsCon.DefaultEastLongitude)
        latentry.set_text(self.ObsCon.LatitudeString())
        lonentry.set_text(self.ObsCon.EastLongitudeString())
        self.DrawEverything()
        return True

# event
    def ChangeLatitude(self,widget,entry):
        self.ObsCon.SetLatitude(string.atof(entry.get_text()))
        entry.set_text(self.ObsCon.LatitudeString())
        self.DrawEverything()
        return True

# event
    def ChangeLongitude(self,widget,entry):
        self.ObsCon.SetEastLongitude(string.atof(entry.get_text()))
        entry.set_text(self.ObsCon.EastLongitudeString())
        self.DrawEverything()
        return True

# event
    def AddDeltaT(self,widget,seconds):
        if (seconds > 0):
            self.ObsCon.SetUTC(self.ObsCon.UTC
                               +datetime.timedelta(0,seconds,0))
        else:
            self.ObsCon.SetUTC(self.ObsCon.UTC
                               -datetime.timedelta(0,-seconds,0))
        self.DrawEverything()
        return True

# event
    def ResetT(self,widget):
        self.ObsCon.ResetUTC()
        self.DrawEverything()
        return True

# event
    def SetAz(self,widget,az):
        self.ObsCon.SetAz(az)
        self.DrawEverything()
        return True

# event
    def AddDeltaAz(self,widget,daz):
        self.ObsCon.SetAz(self.ObsCon.Az+daz)
        self.DrawEverything()
        return True

# event
    def SetAlt(self,widget,alt):
        self.ObsCon.SetAlt(alt)
        self.DrawEverything()
        return True

# event
    def AddDeltaAlt(self,widget,dalt):
        newalt= self.ObsCon.Alt+dalt
        self.ObsCon.SetAlt(newalt)
        self.DrawEverything()
        return True

# event
    def ToggleStarLabels(self,widget):
        if (self.ObsCon.DrawStarLabels == True):
            self.ObsCon.SetDrawStarLabels(False)
        else:
            self.ObsCon.SetDrawStarLabels(True)
        self.DrawEverything()
        return True

# event
    def ToggleCelestialGrid(self,widget):
        if (self.ObsCon.DrawCelestialGrid):
            self.ObsCon.SetDrawCelestialGrid(False)
        else:
            self.ObsCon.SetDrawCelestialGrid(True)
        self.DrawEverything()
        return True

# event
    def ToggleSolarSystemGrid(self,widget):
        if (self.ObsCon.DrawSolarSystemGrid):
            self.ObsCon.SetDrawSolarSystemGrid(False)
        else:
            self.ObsCon.SetDrawSolarSystemGrid(True)
        self.DrawEverything()
        return True

# event
    def ToggleReverseVideo(self,widget):
        if (self.ObsCon.ReverseVideo == True):
            self.ObsCon.SetReverseVideo(False)
        else:
            self.ObsCon.SetReverseVideo(True)
        self.DrawEverything()
        return True

# event
    def RedrawEvent(self,widget):
        self.DrawEverything()
        return True

# project from 3D to 2D plotting plane
    def ProjectStars(self):
        zenith= self.ObsCon.Zenith()
        pp= self.ObsCon.ViewPoint()
        phat= pp.hat()
        pminusphat= pp-phat
        pdotp= pp.dot(pp)
        XX,YY= Normals(phat,zenith)
        XX= -XX
        x,y,width,height = self.DrawingArea.get_allocation()
        for star in self.Stars:
            if (self.ObsCon.ClipHorizon and (star.Vector3.dot(zenith) < 0.0)):
                star.SetVector2(None)
            else:
                star.SetVector2(ProjectVector(star.Vector3,pp,phat,
                                              pminusphat,pdotp,XX,YY,
                                              self.ObsCon.Zoom,width,height))
        for label in self.Labels:
            if (self.ObsCon.ClipHorizon and (label.Vector3.dot(zenith) < 0.0)):
                label.SetVector2(None)
            else:
                label.SetVector2(ProjectVector(label.Vector3,pp,phat,
                                               pminusphat,pdotp,XX,YY,
                                               self.ObsCon.Zoom,width,height))
        for planet in self.Planets:
            if (planet.Name[0:5] == 'Earth'):
                earthvector= planet.Vector3(self.ObsCon.UTC)
                planet.SetVector2(None)
        for planet in self.Planets:
            if (planet.Name[0:5] != 'Earth'):
                deltavector= planet.Vector3(self.ObsCon.UTC)-earthvector
                deltavector= deltavector.hat()
                if (self.ObsCon.ClipHorizon and
                    (deltavector.dot(zenith) < 0.0)):
                    planet.SetVector2(None)
                else:
                    planet.SetVector2(ProjectVector(deltavector,pp,phat,
                                                    pminusphat,pdotp,XX,YY,
                                                    self.ObsCon.Zoom,
                                                    width,height))
                if (planet.Name[0:3] == 'Sun'):
                    sunaltitude= (math.asin(deltavector.dot(zenith))*
                                  piunder180)
# daylight ends when the center of the sun is (16+34) arcmin below the horizon,
#    because of finite size and atmospheric refraction effects.
                    if (sunaltitude > (-50.0/60.0)):
                        self.ObsCon.DaylightString= _('day')
                    elif (sunaltitude > (-6.0)):
                        self.ObsCon.DaylightString= _('civil twilight')
                    elif (sunaltitude > (-18.0)):
                        self.ObsCon.DaylightString= _('astronomical twilight')
                    else:
                        self.ObsCon.DaylightString= _('night')
        for gridpoint in self.Grid:
            gridpoint.SetVector2(ProjectVector(gridpoint.Vector3,pp,phat,
                                               pminusphat,pdotp,XX,YY,
                                               self.ObsCon.Zoom,
                                               width,height))
        return True

# output everything to screen
#     note that order matters for drawing, and drawing order depends on the
#     order of things in the lists of things to draw; local stuff should be
#     *last* by this criterion, because the horizon labels should blot out
#     everything.
    def DrawEverything(self):
        if (self.ObsCon.ReverseVideo):
            graphcon= self.BlackGraphCon
            bggraphcon= self.WhiteGraphCon
        else:
            graphcon= self.WhiteGraphCon
            bggraphcon= self.BlackGraphCon
        self.Labels= []
        self.Grid= []
        if (self.ObsCon.DrawSolarSystemGrid):
            self.Grid+= self.SolarSystemGrid
            self.Labels+= self.SolarSystemGridLabels
        if (self.ObsCon.DrawCelestialGrid):
            self.Grid+= self.CelestialGrid
            self.Labels+= self.CelestialGridLabels
        if (self.ObsCon.DrawHorizon):
            grid,gridlabels= LocalGrid(self.ObsCon.Zenith())
            self.Grid+= grid
            self.Labels+= gridlabels
        self.Labels+= self.CelestialLabels+LocalLabelCatalog(self.ObsCon)
        self.ProjectStars() # project stars and labels and planets
        x,y,width,height = self.DrawingArea.get_allocation()
        self.PixMap.draw_rectangle(bggraphcon,True,0,0,width,height)
        self.DrawGrid(width,height,graphcon)
        self.DrawLabels(width,height,graphcon,bggraphcon)
        self.DrawStars(width,height,graphcon)
        self.PangoLayout.set_markup(self.ObsCon.InfoString())
        pwidth,pheight= self.PangoLayout.get_pixel_size()
        xx, yy= self.BigSpacing, height-self.BigSpacing-pheight
        self.PixMap.draw_rectangle(bggraphcon,True,xx,yy,pwidth,pheight)
        self.PixMap.draw_layout(graphcon,xx,yy,self.PangoLayout)
        self.PangoLayout.set_markup(self.ObsCon.DaylightString)
        pwidth,pheight= self.PangoLayout.get_pixel_size()
        xx, yy= width-self.BigSpacing-pwidth, self.BigSpacing
        self.PixMap.draw_rectangle(bggraphcon,True,xx,yy,pwidth,pheight)
        self.PixMap.draw_layout(graphcon,xx,yy,self.PangoLayout)
        self.DrawingArea.window.draw_drawable(graphcon,self.PixMap,
                                              0,0,0,0,width,height)
        return False

# draw stars
#     assumes ProjectStars() has been run
    def DrawStars(self,width,height,graphcon):
        labeloff= 15 # pix -- must be synchronized with max star size!
        for star in (self.Stars+self.Planets):
            if (star.Vector2 != None):
                fullsize= 3.0*(self.ObsCon.Faintest-star.Vmag)+1.0
                if (fullsize < 0): fullsize= 0
                if (fullsize > (labeloff+labeloff)): fullsize= 2.0*labeloff
                halfsize= int(fullsize/2.0)
                fullsize= int(fullsize+0.5)
                fullsize= halfsize+halfsize+1
                xx= int(star.Vector2[0])
                yy= int(star.Vector2[1])
                self.PixMap.draw_rectangle(graphcon,True,
                                           xx-halfsize,yy-halfsize,
                                           fullsize,fullsize)
                if (self.ObsCon.DrawStarLabels and
                    ((star.Vmag <= 2.0) or
                     (star.DrawLabelEvenIfFaint)) and
                    (star.Name != None)):
                    self.PixMap.draw_line(graphcon,
                                          xx,yy,xx+labeloff,yy+labeloff)
                    self.PangoLayout.set_text(star.Name)
                    self.PixMap.draw_layout(graphcon,
                                            xx+labeloff,yy+labeloff,
                                            self.PangoLayout)

# draw all coordinate grids
#     assumes ProjectStars() has been run
    def DrawGrid(self,width,height,graphcon):
        prevgridpoint= Star(None,None,None,None)
        for gridpoint in self.Grid:
            if ((gridpoint.Name == prevgridpoint.Name) and
                (gridpoint.Vector2 != None) and
                (prevgridpoint.Vector2 != None)):
                self.PixMap.draw_line(graphcon,
                                      int(prevgridpoint.Vector2[0]),
                                      int(prevgridpoint.Vector2[1]),
                                      int(gridpoint.Vector2[0]),
                                      int(gridpoint.Vector2[1]))
            prevgridpoint= gridpoint
        return False

# label points on sphere
#     assumes ProjectStars() has been run
    def DrawLabels(self,width,height,graphcon,bggraphcon):
        for label in self.Labels:
            if (label.Vector2 != None):
                self.PangoLayout.set_markup(label.Name)
                pwidth,pheight= self.PangoLayout.get_pixel_size()
                xx= int(label.Vector2[0]-pwidth/2.0)
                yy= int(label.Vector2[1]-pheight/2.0)
                self.PixMap.draw_rectangle(bggraphcon,True,
                                           xx,yy,pwidth,pheight)
                self.PixMap.draw_layout(graphcon,xx,yy,
                                        self.PangoLayout)

# start GTK loop, waiting for events
    def main(self):
        gtk.main()

def main():
    nightsky = NightSky()
    nightsky.main()

# if we are run as the main program, fire up the planetarium
if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == '--profile':
        import profile
        profile.run('main()')
