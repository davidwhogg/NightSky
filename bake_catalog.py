#!/usr/bin/env python
#-*- coding: utf-8 -*-
##############################################################################
# name:
#   bake_catalog
# purpose:
#   Convert Bright Star Catalog to a python literal.
# to-do items:
#   - proper subscripts for, eg, Alp_1 Cen
# bugs:
#   - Conversion to proper Greek letters is clumsy and brittle.
#   - Incorporation of common names is clumsy and brittle.
# dependencies:
#   - sys ?
#   - string
# author:
#   David W. Hogg (New York University) http://cosmo.nyu.edu/hogg/
#   - Hogg gratefully acknowledges help from Keir Mierle (U of Toronto).
# license:
#   TBD
# revision history:
#   2007-01-28  basically works - Hogg
#   2007-08-07  hacked to add C output -dstn
###############################################################################

import sys
import string

# read catalog
def BrightStarCatalog(faintest, cmode):
    file= open("bright_star_catalog_v50")
    bsc= []
    for line in file:
        if (string.strip(line[75:77]) != ""):
            Vmag= string.atof(line[102:106])
            if (Vmag < faintest):
                ra= 15.0*(string.atof(line[75:77])
                         +string.atof(line[77:79])/60.0
                         +string.atof(line[79:83])/3600.0)
                dec= (string.atof(line[84:86])
                     +string.atof(line[86:88])/60.0
                     +string.atof(line[88:90])/3600.0)
                if (line[83] == '-'):
                    dec= -dec
                name= string.strip(line[7:14])
                common= None

                                # Fix "16  Tau", etc.
                if (len(name) == 3):
                    name = ("%-3i" % (int)(string.strip(line[4:7]))) + ' ' + name

                # In Firefox, go to http://www.obliquity.com/skyeye/misc/name.html
                # select the table of names, and pipe it through:
                '''
                #! /bin/bash
                awk 'BEGIN{FS="\t"} {print "\"" $2 "\" : \"" $1 "\""}' | \
                sed -e 's/^"alpha/"Alp/' -e 's/^"beta/"Bet/' -e 's/^"gamma/"Gam/' -e 's/^"delta/"Del/' -e 's/^"epsilon/"Eps/' -e 's/^"zeta/"Zet/' -e 's/^"eta/"Eta/' -e 's/^"theta/"The/' -e 's/^"iota/"Iot/' -e 's/^"kappa/"Kap/' -e 's/^"lambda/"Lam/' -e 's/^"mu/"Mu/' -e 's/^"nu/"Nu/' -e 's/^"xi/"Xi/' -e 's/^"omicron/"Omi/' -e 's/^"pi/"Pi/' -e 's/^"rho/"Rho/' -e 's/^"sigma/"Sig/' -e 's/^"tau/"Tau/' -e 's/^"upsilon/"Ups/' -e 's/^"phi/"Phi/' -e 's/^"psi/"Psi/' -e  's/^"omega/"Ome/' |
                sed -e 's/Andromedae/And/' -e 's/Antlia/Ant/' -e 's/Apus/Aps/' -e 's/Aquarii/Aqr/' -e 's/Aquilae/Aql/' -e 's/Ara/Ara/' -e 's/Arietis/Ari/' -e 's/Aurigae/Aur/' -e 's/Bo%Gï¿½%@tes/Boo/' -e 's/Caelum/Cae/' -e 's/Camelopardalis/Cam/' -e 's/Cancri/Cnc/' -e 's/Canum Venaticorum/CVn/' -e 's/Canis Majoris/CMa/' -e 's/Canis Minor/CMi/' -e 's/Capricorni/Cap/' -e 's/Carinae/Car/' -e 's/Cassiopeiae/Cas/' -e 's/Centauri/Cen/' -e 's/Cephei/Cep/' -e 's/Ceti/Cet/' -e 's/Chamaeleon/Cha/' -e 's/Circinus/Cir/' -e 's/Columbae/Col/' -e 's/Coma Berenices/Com/' -e 's/Corona Austrina/CrA/' -e 's/Coronae Borealis/CrB/' -e 's/Corvi/Crv/' -e 's/Crateris/Crt/' -e 's/Crucis/Cru/' -e 's/Cygni/Cyg/' -e 's/Delphini/Del/' -e 's/Dorado/Dor/' -e 's/Draconis/Dra/' -e 's/Equulei/Equ/' -e 's/Eridani/Eri/' -e 's/Fornax/For/' -e 's/Geminorum/Gem/' -e 's/Gruis/Gru/' -e 's/Herculis/Her/' -e 's/Horologium/Hor/' -e 's/Hydra/Hya/' -e 's/Hydrae/Hyi/' -e 's/Indus/Ind/' -e 's/Lacerta/Lac/' -e 's/Leonis/Leo/' -e 's/Leo Minor/LMi/' -e 's/Leporus/Lep/' -e 's/Libra/Lib/' -e 's/Lupus/Lup/' -e 's/Lynx/Lyn/' -e 's/Lyrae/Lyr/' -e 's/Mensa/Men/' -e 's/Microscopium/Mic/' -e 's/Monoceros/Mon/' -e 's/Musca/Mus/' -e 's/Norma/Nor/' -e 's/Octans/Oct/' -e 's/Ophiuchi/Oph/' -e 's/Orionis/Ori/' -e 's/Pavonis/Pav/' -e 's/Pegasi/Peg/' -e 's/Persei/Per/' -e 's/Phoenicis/Phe/' -e 's/Pictor/Pic/' -e 's/Piscium/Psc/' -e 's/Piscis Austrini/PsA/' -e 's/Puppis/Pup/' -e 's/Pyxis/Pyx/' -e 's/Reticulum/Ret/' -e 's/Sagitta /Sge /' -e 's/Sagittarii/Sgr/' -e 's/Scorpii/Sco/' -e 's/Sculptor/Scl/' -e 's/Scutum/Sct/' -e 's/Serpentis/Ser/' -e 's/Sextans/Sex/' -e 's/Tauri/Tau/' -e 's/Telescopium/Tel/' -e 's/Trianguli/Tri/' -e 's/Triangulum Australe/TrA/' -e 's/Tucana/Tuc/' -e 's/Ursae Majoris/UMa/' -e 's/Ursae Minoris/UMi/' -e 's/Velorum/Vel/' -e 's/Virginis/Vir/' -e 's/Volans/Vol/' -e 's/Vulpecula/Vul/' 
                '''
                # then hand-edit a bit.
                common_names = {
                    "16  Tau" : "Celaeno",
                    "17  Tau" : "Electra",
                    "19  Tau" : "Taygeta",
                    "20  Tau" : "Maia",
                    "21  Tau" : "Sterope I",
                    "22  Tau" : "Sterope II",
                    "23  Tau" : "Merope",
                    "27  Tau" : "Atlas",
                    "28  Tau" : "Pleione",
                    "80  UMa" : "Alcor",
                    "Alp1Her" : "Rasalgethi",
                    "Alp2Lib" : "Zubenelgenubi",
                    "Alp And" : "Alpheratz",
                    "Alp Aql" : "Altair",
                    "Alp Aqr" : "Sadalmelik",
                    "Alp Ari" : "Hamal",
                    "Alp Aur" : "Capella",
                    "Alp Boo" : "Arcturus",
                    "Alp Cap" : "Algedi",
                    "Alp Car" : "Canopus",
                    "Alp Cas" : "Schedar",
                    "Alp Cen" : "Rigil Kent(aurus)",
                    "Alp Cep" : "Alderamin",
                    "Alp Cet" : "Menkab / Menkar",
                    "Alp CMa" : "Sirius",
                    "Alp CMi" : "Procyon",
                    "Alp Cnc" : "Acubens",
                    "Alp Col" : "Phact",
                    "Alp CrB" : "Alphecca / Gemma",
                    "Alp Crt" : "Alkes",
                    "Alp Cru" : "Acrux",
                    "Alp Crv" : "Alchiba",
                    "Alp CVn" : "Cor Caroli",
                    "Alp Cyg" : "Deneb",
                    "Alp Del" : "Sualocin",
                    "Alp Dra" : "Thuban",
                    "Alp Equ" : "Kitalpha",
                    "Alp Eri" : "Achernar / Archenar",
                    "Alp Gem" : "Castor",
                    "Alp Gru" : "Al Na'ir",
                    "Alp Hya" : "Alphard",
                    "Alp Leo" : "Regulus",
                    "Alp Lep" : "Arneb",
                    "Alp Lyr" : "Vega",
                    "Alp Oph" : "Rasalhague",
                    "Alp Ori" : "Betelgeuse",
                    "Alp Pav" : "Peacock",
                    "Alp Peg" : "Markab",
                    "Alp Per" : "Mirfak",
                    "Alp Phe" : "Ankaa",
                    "Alp PsA" : "Fomalhaut",
                    "Alp Psc" : "Alrescha",
                    "Alp Sco" : "Antares",
                    "Alp Ser" : "Unukalhai",
                    "Alp Sgr" : "Rukbat",
                    "Alp Tau" : "Aldebaran",
                    "Alp TrA" : "Atria",
                    "Alp Tri" : "Mothallah",
                    "Alp UMa" : "Dubhe",
                    "Alp UMi" : "Polaris",
                    "Alp Vir" : "Spica",
                    "Bet1Cyg" : "Albireo",
                    "Bet1Sco" : "Graffias",
                    "Bet And" : "Mirach",
                    "Bet Aql" : "Alshain",
                    "Bet Aqr" : "Sadalsuud",
                    "Bet Ari" : "Sheratan",
                    "Bet Aur" : "Menkalinan",
                    "Bet Boo" : "Nekkar",
                    "Bet Cap" : "Dabih",
                    "Bet Car" : "Miaplacidus",
                    "Bet Cas" : "Caph",
                    "Bet Cen" : "Agena / Hadar",
                    "Bet Cep" : "Alfirk",
                    "Bet Cet" : "Deneb Kaitos / Diphda",
                    "Bet CMa" : "Mirzam",
                    "Bet CMi" : "Gomeisa",
                    "Bet Col" : "Wazn",
                    "Bet CrB" : "Nusakan",
                    "Bet Cru" : "Becrux / Mimosa",
                    "Bet CVn" : "Chara",
                    "Bet Del" : "Rotanev",
                    "Bet Dra" : "Rastaban",
                    "Bet Eri" : "Cursa",
                    "Bet Gem" : "Pollux",
                    "Bet Her" : "Kornephoros",
                    "Bet Leo" : "Denebola",
                    "Bet Lep" : "Nihal",
                    "Bet Lib" : "Zubeneschamali",
                    "Bet Lyr" : "Sheliak",
                    "Bet Oph" : "Cebalrai / Cheleb",
                    "Bet Ori" : "Rigel",
                    "Bet Peg" : "Scheat",
                    "Bet Per" : "Algol",
                    "Bet Sgr" : "Arkab",
                    "Bet Tau" : "Elnath / El Nath",
                    "Bet UMa" : "Merak",
                    "Bet UMi" : "Kochab",
                    "Bet Vir" : "Zavijava",
                    "Del Aqr" : "Skat",
                    "Del Cap" : "Deneb Algedi",
                    "Del Cas" : "Ruchbah",
                    "Del CMa" : "Wezen",
                    "Del Cnc" : "Asellus Australis",
                    "Del Crv" : "Algorab",
                    "Del Dra" : "Altais",
                    "Del Gem" : "Wasat",
                    "Del Leo" : "Zosma",
                    "Del Oph" : "Yed Prior",
                    "Del Ori" : "Mintaka",
                    "Del Sco" : "Dschubba",
                    "Del Sgr" : "Kaus Media / Kaus Meridianalis",
                    "Del Sgr" : "Media",
                    "Del UMa" : "Megrez",
                    "Del UMi" : "Yildun",
                    "Eps Aqr" : "Albali",
                    "Eps Boo" : "Izar / Pulcherrima",
                    "Eps Car" : "Avior",
                    "Eps Cas" : "Navi",
                    "Eps CMa" : "Adhara / Adara",
                    "Eps Cyg" : "Gienah",
                    "Eps Gem" : "Mebsuta",
                    "Eps Leo" : "Ras Elased",
                    "Eps Oph" : "Yed Posterior",
                    "Eps Ori" : "Alnilam",
                    "Eps Peg" : "Enif",
                    "Eps Sgr" : "Kaus Australis",
                    "Eps UMa" : "Alioth",
                    "Eps Vir" : "Vindemiatrix",
                    "Eta Boo" : "Muphrid",
                    "Eta CMa" : "Aludra",
                    "Eta Eri" : "Azha",
                    "Eta Gem" : "Propus",
                    "Eta Oph" : "Sabik",
                    "Eta Peg" : "Matar",
                    "Eta UMa" : "Alkaid / Benetnasch",
                    "Eta Vir" : "Zaniah",
                    "Gam1And" : "Almach",
                    "Gam1Leo" : "Algieba",
                    "Gam2Ari" : "Mesarthim",
                    "Gam2Sgr" : "Alnasl",
                    "Gam Aql" : "Tarazed",
                    "Gam Aqr" : "Sadalachbia",
                    "Gam Boo" : "Seginus",
                    "Gam Cap" : "Nashira",
                    "Gam Cen" : "Muhlifain",
                    "Gam Cep" : "Errai",
                    "Gam CMa" : "Muliphen",
                    "Gam Cnc" : "Asellus Borealis",
                    "Gam Cru" : "Gacrux",
                    "Gam Crv" : "Gienah",
                    "Gam Cyg" : "Sadr",
                    "Gam Dra" : "Eltanin",
                    "Gam Eri" : "Zaurak",
                    "Gam Gem" : "Alhena",
                    "Gam Lyr" : "Sulafat",
                    "Gam Ori" : "Bellatrix",
                    "Gam Peg" : "Algenib",
                    "Gam UMa" : "Phad / Phecda",
                    "Gam UMi" : "Pherkad",
                    "Gam Vel" : "Regor",
                    "Gam Vir" : "Porrima",
                    "Iot Car" : "Aspidiske",
                    "Iot Dra" : "Edasich",
                    "Iot UMa" : "Dnoces / Talitha",
                    "Iot Vir" : "Syrma",
                    "Kap Aqr" : "Situla",
                    "Kap Ori" : "Saiph",
                    "Lam Dra" : "Giausar",
                    "Lam Leo" : "Alterf",
                    "Lam Oph" : "Marfik",
                    "Lam Ori" : "Meissa",
                    "Lam Sco" : "Shaula",
                    "Lam Sgr" : "Kaus Borealis",
                    "Lam UMa" : "Tania Borealis",
                    "Lam Vel" : "Suhail",
                    "Mu 1Boo" : "Alkalurops",
                    "Mu  Cep" : "Garnet Star",
                    "Mu  Col" : "Runaway Star",
                    "Mu  Peg" : "Sadalbari",
                    "Mu  UMa" : "Tania Australis / Alula Borealis",
                    "Ome3Cyg" : "Ruchba",
                    "Omi1Eri" : "Beid",
                    "Omi2Eri" : "Keid",
                    "Omi Cet" : "Mira",
                    "Omi UMa" : "Muscida",
                    "Sig Sco" : "Al Niyat",
                    "Sig Sgr" : "Nunki",
                    "Tau Tau" : "Alcyone",
                    "The1Eri" : "Acamar",
                    "The1Ser" : "Alya",
                    "The Aqr" : "Ancha",
                    "The Cen" : "Menkent",
                    "The Leo" : "Chertan / Chort",
                    "The Peg" : "Biham",
                    "The Sco" : "Girtab / Sargas",
                    "Ups Sco" : "Lesath",
                    "Xi  Dra" : "Grumium",
                    "Xi  UMa" : "Alula Australis",
                    "Zet1Cnc" : "Tegmine",
                    "Zet Aur" : "Sadatoni",
                    "Zet Cet" : "Baten Kaitos",
                    "Zet CMa" : "Furud",
                    "Zet Gem" : "Mekbuda",
                    "Zet Leo" : "Adhafera",
                    "Zet Ori" : "Alnitak",
                    "Zet Peg" : "Homam",
                    "Zet Per" : "Atik",
                    "Zet Pup" : "Naos",
                    "Zet Sgr" : "Ascella",
                    "Zet UMa" : "Mizar",
                    }

                if common_names.has_key(name):
                    common = common_names[name];

                if (len(name) == 7):
                    # Greek letter: 'Alp', 'Bet', ...
                    letter = name[0:3];

                    # The constellation abbreviation (CMa, And, ...)
                    rest = name[3:7];

                    # Python unicode string
                    python_greek = {
                        'Alp' : '\u03B1',
                        'Bet' : '\u03B2',
                        'Gam' : '\u03B3',
                        'Del' : '\u03B4',
                        'Eps' : '\u03B5',
                        'Zet' : '\u03B6',
                        'Eta' : '\u03B7',
                        'The' : '\u03B8',
                        'Iot' : '\u03B9',
                        'Kap' : '\u03BA',
                        'Lam' : '\u03BB',
                        'Mu ' : '\u03BC',
                        'Nu ' : '\u03BD',
                        'Xi ' : '\u03BE',
                        'Omi' : '\u03BF',
                        'Pi ' : '\u03C0',
                        'Rho' : '\u03C1',
                        'Sig' : '\u03C3',
                        'Tau' : '\u03C4',
                        'Ups' : '\u03C5',
                        'Phi' : '\u03C6',
                        'Chi' : '\u03C7',
                        'Psi' : '\u03C8',
                        'Ome' : '\u03C9', };

                    # Hack... I couldn't figure out how to derive these bytes from the unicode strings above.
                    c_greek = {
                        'Alp' : '\xCE\xB1',
                        'Bet' : '\xCE\xB2',
                        'Gam' : '\xCE\xB3',
                        'Del' : '\xCE\xB4',
                        'Eps' : '\xCE\xB5',
                        'Zet' : '\xCE\xB6',
                        'Eta' : '\xCE\xB7',
                        'The' : '\xCE\xB8',
                        'Iot' : '\xCE\xB9',
                        'Kap' : '\xCE\xBA',
                        'Lam' : '\xCE\xBB',
                        'Mu ' : '\xCE\xBC',
                        'Nu ' : '\xCE\xBD',
                        'Xi ' : '\xCE\xBE',
                        'Omi' : '\xCE\xBF',
                        'Pi ' : '\xCF\x80',
                        'Rho' : '\xCF\x81',
                        'Sig' : '\xCF\x83',
                        'Tau' : '\xCF\x84',
                        'Ups' : '\xCF\x85',
                        'Phi' : '\xCF\x86',
                        'Chi' : '\xCF\x87',
                        'Psi' : '\xCF\x88',
                        'Ome' : '\xCF\x89', };

                    if not(cmode) and python_greek.has_key(letter):
                        name = python_greek[letter] + rest

                    if cmode and c_greek.has_key(letter):
                        name = c_greek[letter].encode('string_escape') + "\" \"" + rest
                        #import unicodedata
                        #strng = python_greek[letter]
                        #uc = (unicode)(strng[0])
                        #name = unicodedata.digit(uc) + rest
                        #name = c_greek[letter].encode('string_escape') + "\" \"" + rest

                name= name.replace(" ","")

                if cmode:
                    commonstr = ""
                    if common:
                        commonstr = common
                    bsc.append((name, commonstr, ra, dec, Vmag))
                else:
                    if (common == None):
                        if ((name == None) | (name == "")): name= "None"
                        else: name= "ur'%s'" % name
                    else:
                        common= common.replace("'","\\'")
                        name= "_('%s')+ur' (%s)'" % (common,name)
                    bsc.append((name,ra,dec,Vmag))
    return bsc

def MakeSelfContainedStarCatalogAndNightsky(outfilename, faintest, cmode):
    bsc = BrightStarCatalog(faintest, cmode)
    out = []
    if cmode:
        out.append('// Autogenerated by bake_catalog.py\n')
        out.append('{')
        for star in bsc:
            out.append("{ \"%s\", \"%s\", %8.4f, %8.4f, %4.1f }," % star)
        out.append('}\n')
    else:
        out.append('LiteralBrightStarCatalog = (')
        for star in bsc:
            out.append("(%s,%8.4f,%+8.4f,%4.1f)," % star)
        out.append(')\n')
    outfile = file(outfilename, 'w')
    outfile.write('\n'.join(out))
    outfile.close()

# if we are run as the main program, fire up the oven and bake
if __name__ == "__main__":
    cmode = 0
    if (len(sys.argv) == 2) and (sys.argv[1] == '-c'):
        cmode = 1
    elif len(sys.argv) != 1:
        # no help for you!
        sys.exit(-1);
    outfilename = sys.argv[0].replace('.py','');
    MakeSelfContainedStarCatalogAndNightsky(outfilename, 5.0, cmode)
