import bottle
from random import *
from bottle import route, run, template,request
from html.entities import codepoint2name
import xml.etree.ElementTree as ET
import requests 
from bs4 import BeautifulSoup
import json
#import sage.graphs.graph
from geopy.geocoders import Nominatim
from geopy.exc import  GeocoderTimedOut

from folium import Map, Marker
tree = ET.parse('Auteur/Lélia_Blin.xml')
root=tree.getroot() 

json_data = json.load(open('coreconf.json'))

def htmlCoding(stringToCode): 
    return ''.join( '&%s;' % codepoint2name[ord(oneChar)]                   
                                            if ord(oneChar) in codepoint2name                    
                                            else oneChar for oneChar in stringToCode) 
@route("/")
def index():
    return template('accueil.tpl')
# refaire le error avec plus info
@route("/error/")
def error():
    error = " Ce que vous demandez n'est pas accesible"
    return error

"""------------------------------- Question 1 ----------------------------------------"""

@route("/authors/Qui") 
def qui():
    return template('formulaire.tpl',auteur="/authorsURL/nom/prenom", titre="Rechercher D'auteur")

@route("/authors/Journal/Qui") 
def quiJournal():
    return template('formulaire.tpl',auteur="/authorsURLJournal/Journals/nom/prenom",titre="Rechercher de Journal")

@route("/authors/Conference/Qui") 
def quiConf():
    return template('formulaire.tpl',auteur="/authorsURLConf/Conference/nom/prenom",titre="Rechercher de Conference")



def lastname():
    nom= request.forms.nom
    nom=nom.replace(" ","_")
    nom=nom.replace(".","=")
    return nom

def firstname():
    prenom = request.forms.prenom
    prenom=prenom.replace(" ","_")
    prenom=prenom.replace(".","=")
    return prenom

def verification():
     for child in root:
        if child.tag == "person":
            for flags in child:
                if flags.tag == "author":
                    return flags.text
    
@route("/authorsURL/<nom>/<prenom>", method='POST')
def authorsURL(nom,prenom):
     nom= lastname()
     prenom = firstname()
     flags = verification() 
     tab = flags.split(" ")
     if prenom == tab[0] and nom == tab[-1]:
       name="/authors/"+nom+'/'+prenom
       bottle.redirect(name)
     else:
       bottle.redirect("/error/")

@route("/authorsURLConf/Conference/<nom>/<prenom>", method='POST')
def authorsURLConf(nom,prenom):
    nom= lastname()
    prenom = firstname()
    name = prenom + "" + nom
    
    flags = verification()
    tab = flags.split(" ")
    if prenom == tab[0] and nom == tab[-1] :
       name="/authors/Conference/"+nom+'/'+prenom
       bottle.redirect(name)
    else:
        bottle.redirect("/error/")
                               
        
@route("/authorsURLJournal/Journals/<nom>/<prenom>", method='POST')
def authorsURLJournal(nom,prenom):
    nom= lastname()
    prenom = firstname()
    name = prenom + "" + nom
    flags= verification()
    tab = flags.split(" ")
    if prenom == tab[0] and nom == tab[-1]:
        name="/authors/Journals/"+nom+'/'+prenom
        bottle.redirect(name)

    else:
        bottle.redirect("/error/")

"""-----------------------------------Question 3-------------------------"""
@route("/authors/Journals/Synthese/<nom>/<prenom>")
def Article(nom,prenom):
    dicto={}
    tabTitre = []
    tabYear=[]
    tabJournal=[]
    tabClassement=[]
    dictionnairefinal={}
    for child in root:
         for childs in child:
             if (childs.tag == 'article'):
                 for flags in childs: 
                    if (flags.tag== 'url'):
                        url=flags.text
                        dictionnairefinal[url]='No Ranks'
                        url2="https://dblp.uni-trier.de/"+url
                        r = requests.get(url2)
                        soup = BeautifulSoup(r.content,"html.parser")
                        annuaire = str(soup.find('title'))
                        annuaire=annuaire.replace("</title>","")
                        annuaire=annuaire.replace("<title>","")
                        annuaire=annuaire.replace("dblp:","")
                        acrony= annuaire.split(",")
                        infos=acrony[0]
                        url3= "http://portal.core.edu.au/jnl-ranks/?search="+infos+"&by=all&source=all&sort=atitle&page=1"
                        r2 = requests.get(url3)
                        soup2 = BeautifulSoup(r2.content,"html.parser")
                        #td =soup2.find_all('td')
                        #liste=[]
                        infos=str(infos)
                        l = soup2.find_all('tr')
                        infos=infos.replace("'","")
                    #    print(infos)
                        tabJournal.append(infos)
                        for j in l:
                           lestds = j.find_all('td')
                           c=0
                           for i in lestds:
                               i=i.string
                               i=i.split()
                               infos2=infos.split()
                               c+=1
                               if (c==1):
                                   titre=i
                                 #  print(titre)
                                 #  print(infos2)
                               if (c==3):
                                   classement=i
                                   if(titre==infos2):
                                       titrefinal= ' '.join(titre)
                                    #   print(titrefinal)
                                    #   print("okey")
                                       dicto[titrefinal]=classement
                                       dictionnairefinal[url]=classement
                                  
                                    
                    
                    elif (flags.tag == 'title'):
                        title = flags.text 
                    elif (flags.tag == 'year'):
                        year =flags.text
                    elif (flags.tag == "journal"):
                        tabTitre.append(title)
                        tabYear.append(year)

                        
    
                        
    #print(dicto)
    

    for clasm in dictionnairefinal.values():
        tabClassement.append(clasm)


            
    stri = "<h1>" + nom + prenom +  "</h1> "
    stri += "<h2> <center> Synthèse pour les journaux</centre> </h2>  <hr/>"
    stri += """<table>"""
    stri += """<thead>""" 
    stri += """<tr>
           <th>Titre</th>
           <th>Years</th>
           <th>Ref</th>
           <th>Classement</th>
           
       </tr>
   </thead>"""
    
    stri+= "<tbody>"
    for i in range (0,len(tabTitre)-1):
        stri+= "<tr>"
        ligne = str(tabTitre[i])
        ligne2 =str(tabYear[i]) 
        ligne3=str(tabJournal[i])
        ligne4=str(tabClassement[i])

        stri+= "<td>"+ligne+"</td>"
        stri+= "<td>"+ligne2+"</td>"
        stri+= "<td> <center>"+ligne3+" </center></td>"
        stri+= "<td>"+ligne4+"</td>"
        stri+= "</tr>"

    stri+= "</tbody>"   
    stri+= "</table>"
    return stri

        
"""------------------------------------Question 4 ------------------------"""        
def getAllInfo():
    tab = []
    for child in root:
         for childs in child:
             tabAuteur= []
             if (childs.tag == 'article'):
                 getAllInfoChilds(childs,tab,tabAuteur)
    return tab

def getAllInfoChilds(article,tab,tabAuteur):
     for flags in article:
        if flags.tag  == "author":
            tabAuteur.append(flags.text)
        elif (flags.tag == 'title'):
            title = flags.text 
        elif (flags.tag == 'year'):
            year =flags.text
        elif (flags.tag == "journal"):
           tab.append((title,year,flags.text,tabAuteur))


@route("/authors/Journals/<nom>/<prenom>")
def journals(nom,prenom):
    tab =  getAllInfo()
    stri = "<h1>" + nom + " " + prenom + "</h1> "
    stri += "<h2> <center> Journal </centre> </h2>  <hr/>"
    stri+= "<td>    </td>"
    stri += """<table style ="ont-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;">"""
    for i in range (0,len(tab)-1):
        stri+= """<tr>"""
        ligne = str(tab[i])
        ligne = ligne.replace("(","")
        ligne = ligne.replace(",","|")
        ligne = ligne.replace("'"," ")
        ligne = ligne.replace(")","")
        ligne = ligne.replace("[","")
        ligne = ligne.replace("]","")
        stri+= """<th style =" border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;">"""+ligne+"</th>"
        stri+= "</tr>"
    stri+= "</table>"
    return stri

"""-------------------------------------Question 5----------------------------"""
@route("/authors/Conference/Synthese/<nom>/<prenom>")
def Conference(nom,prenom):
    tabTitre = []
    tabYear=[]
    tabRef=[]
    tabClassement=[]
    mon_dictionnaire = {}
    for child in root:
         for childs in child:
             if (childs.tag == 'inproceedings'):
                 for flags in childs:
                    if (flags.tag == 'title'):
                        title = flags.text 
                    elif (flags.tag == 'year'):
                        year =flags.text
                    elif (flags.tag == "booktitle"):
                        tabTitre.append(title)
                        tabYear.append(year)
                        tabRef.append(flags.text)
                        
    try:
            for x in json_data :
                classement =x['Unranked']
                acronyme=x['ACML']
                mon_dictionnaire[acronyme]=classement
            
            
    except(ValueError,KeyError,TypeError):
        print('JSON format error')
        

    
    for j in tabRef:
        acrosearch = str(j)
        if (acrosearch in mon_dictionnaire.keys()):
            valeur= mon_dictionnaire.get(acrosearch)
            tabClassement.append(valeur)

        else:
             tabClassement.append('No Rank')

    stri = "<h1>" + nom +" " + prenom+  "</h1> "
    stri += "<h2> <center> Synthése pour les conferences </centre> </h2>  <hr/>"
    stri += """<table>"""
    stri += """<thead>""" 
    stri += """<tr>
           <th>Titre</th>
           <th>Years</th>
           <th>Ref</th>
           <th>Classement</th>
           
       </tr>
   </thead>"""
    stri+= "<tbody>"
    for i in range (0,len(tabTitre)-1):
        stri+= "<tr>"
        ligne = str(tabTitre[i])
        ligne2 =str(tabYear[i]) 
        ligne3=str(tabRef[i])
        ligne4=str(tabClassement[i])
        stri+= "<td>"+ligne+"</td>"
        stri+= "<td>"+ligne2+"</td>"
        stri+= "<td> <center>"+ligne3+" </center></td>"
        stri+= "<td>"+ligne4+"</td>"
        stri+= "</tr>"
        
    stri+= "</tbody>"   
    stri+= "</table>"
    return stri
       

"""------------------------------------- Question 6 ----------------------------"""
def getAllInfoConf():
    tab = []
    for child in root:
         for childs in child:
             tabAuteur= []
             if (childs.tag == 'inproceedings'):
                 getAllInfoC(childs,tab,tabAuteur)
    return tab

def getAllInfoC(conference,tab,tabAuteur):
     for flags in conference:
        if flags.tag  == "author":
            tabAuteur.append(flags.text)
        elif (flags.tag == 'title'):
            title = flags.text
        elif (flags.tag == 'year'):
            year =flags.text
        elif (flags.tag == "booktitle"):
           tab.append((title,year,flags.text,tabAuteur))

@route("/authors/Conference/<nom>/<prenom>")
def conference(nom,prenom):
    tab = getAllInfoConf()
    stri = "<h1>" + nom +   " " + prenom + "</h1> "
    stri += "<h2> <center> Conference </centre> </h2>  <hr/>"
    stri += "<a href=/authors/Conferences/Voyages/"+nom+"/"+prenom+"> Voyage </a>"
    stri += """<table>"""
    for i in range (0,len(tab)-1):
        stri+= "<tr>"
        ligne = str(tab[i])
        ligne = ligne.replace("(","")
        ligne = ligne.replace(",","|")
        ligne = ligne.replace("'"," ")
        ligne = ligne.replace(")","")
        ligne = ligne.replace("[","")
        ligne = ligne.replace("]","")
        stri+= "<td>"+ligne+"</td>"
        stri+= "</tr>"
    stri+= "</table>"
    return stri

"""--------------------------------------------Question 7 ----------------------------"""
@route("/authors/Conferences/Voyages/<nom>/<prenom>")
def carte(nom,prenom):
    tablieu=[]
    tabAcro=[]
    listecoord=[]   
    for child in root:
         for childs in child:
             if (childs.tag == 'inproceedings'):
                for  conference in childs:
                    if (conference.tag == "url"):
                        url =conference.text 
                        url2="https://dblp.uni-trier.de/"+url
                        r = requests.get(url2)
                        soup = BeautifulSoup(r.content,"html.parser")
                        annuaire = str(soup.find('h1'))
                        annuaire=annuaire.replace("</h1>","")
                        annuaire=annuaire.replace("<h1>","")
                        acrony= " ".join(annuaire.split()[3])
                        infos = " ".join(annuaire.split()[3:])
                        tablieu.append(infos)
                        tabAcro.append(acrony)
                      
    
    for i in tablieu:
        try :
            geolocator = Nominatim(user_agent="specify_your_app_name_here")
            ville = geolocator.geocode(i,   timeout =None )
            listecoord.append((ville.latitude,ville.longitude))
        except GeocoderTimedOut :
              print("error")
              
                
                
    map = Map(location= listecoord[0], tiles='OpenStreetMap', zoom_start=5)
    Marker(location=listecoord[0],popup='conference').add_to(map)
    
    for i in listecoord[1:]:
        Marker(location=i,popup='conference').add_to(map)
    map.save(outfile='map.html')
    ouverture= open('map.html','rb')
    return ouverture

            
"""---------------------------------------------Question 8 ----------------------------"""
def getAllInfoCoAuteur(nom,prenom):
    tab = []
    for child in root:
         for childs in child:
                 for flags in childs:
                     getAllCoAuteur(nom,prenom,flags,tab)
    return tab
                     
def getAllCoAuteur(nom,prenom,flags,tab):
    nom=nom.replace("_"," ")
    nom=nom.replace("=",".")
    prenom=prenom.replace("_"," ")
    prenom=prenom.replace("=",".")
    if (flags.tag == 'author' and flags.text !=nom):
        lesauteurs = flags.text
        if lesauteurs not in tab:
            tab.append(lesauteurs)
            
@route("/authors/Coauthors/synthese/<nom>/<prenom>")
def Coauthors(nom,prenom):
    tab = getAllInfoCoAuteur(nom,prenom)
    stri = "<h1>" + nom + " " + prenom +"</h1> "
    stri += "<h2> <center> Coauthors </centre> </h2>  <hr/>"
    stri += """<table>"""
    for i in range (0,len(tab)-1):
        stri+= "<tr>"
        ligne = str(tab[i])
        ligne = ligne.replace("(","")
        ligne = ligne.replace(",","|")
        ligne = ligne.replace("'"," ")
        ligne = ligne.replace(")","")
        stri+= "<td>"+ligne+"</td>"
        stri+= "</tr>"
    stri+= "</table>"
    return stri    
"""---------------------------------------------- Question 9 --------------------------------------"""
@route("/Conference/Laquelle")
def conferenceform():
    return template('formulaire_acronyme.tpl',titre =  "Recherche par Acronyme" , url="/ConferenceURL/Lieux/conf" )

@route("/ConferenceURL/Lieux/<conf>", method='POST')
def conferenceURL(conf):
    conf = request.forms.search
    name = "/Conference/Lieux/"+conf
    print(name)
    bottle.redirect(name)
    
"""----------------------------------------------Question 10 ------------------------------------------"""
    
@route("/Conference/Lieux/<conf>")
def lieux(conf):
        url = "https://dblp.uni-trier.de/db/conf/"+conf+"/"
        r = requests.get(url)
        soup = BeautifulSoup(r.content,"html.parser")
        body = soup.find('body')
        div = body.find('div',attrs={'id':'main'})
        header = div.find_all('header',attrs={'class':not['headline noline']})
        pays = ""
        coord = []
        countries = []
        for i in header:
           country = str(i.find('h2'))
           country = country.replace("</h2>"," ")
           country = country.replace("<h2>"," ")
           pays += str(country)
           print(pays)
           countries.append(country)
           result = ' '.join(country.split()[4:])
           try :
               geolocator = Nominatim(user_agent="specify_your_app_name_here")
               location = geolocator.geocode(result, timeout= None)
               if location is not None and location.longitude is not None:
                print(str(location.latitude) + " " + str(location.longitude))
                coord.append((location.latitude , location.longitude))
           except GeocoderTimedOut :
              print("error")
              
        map = Map(location=coord[0], tiles='OpenStreetMap', zoom_start=5) 
        Marker(location=coord[0],popup=countries[0]).add_to(map) 
        for i,j in zip(coord[1:],countries[1:]):
           Marker(location=i,popup=j).add_to(map) 
        map.save(outfile='map.html')
        ouverture = open("map.html","rb")
        return ouverture



"""-----------------------------------------------Question 11 ------------------------------------"""

@route("/LIP6")
def lip6():
    tab=[]
    tab2 = []
    tab3 = []
    fd =open('permanents_lip6.txt')
   # G= graph.WhellGraph(tab)
    for line in fd.readlines():
        nom=line.strip()
        tab.append(nom)
    nomauhasard=choice(tab)
    premiere=nomauhasard[0]
    premiere = premiere.lower()
    while True:
            nomauhasard2=choice(tab)
            if nomauhasard != nomauhasard2 :
                premiere1=nomauhasard2[0]
                premiere1 = premiere1.lower()
                break

    nomauhasard = nomauhasard.replace("é","=eacute=")
    nomauhasard = nomauhasard.replace("è","=egrave=")
    nomauhasard = nomauhasard.replace("ê","=ecirc=")
    nomauhasard = nomauhasard.replace("ç","=ccedil=")
    nomauhasard = nomauhasard.replace("ô","=ocirc=")
    nomauhasard = nomauhasard.replace("-","=")
    nomauhasard = nomauhasard.replace(" ",":")
    url = "https://dblp.uni-trier.de/pers/hd/"+premiere+"/"+nomauhasard
    url1 = "https://dblp.uni-trier.de/pers/hd/"+premiere1+"/"+nomauhasard2
    print(url)
    print(url1)
    r = requests.get("https://dblp.uni-trier.de/pers/hd/b/Blin:L=eacute=lia")
    r1 = requests.get("https://dblp.uni-trier.de/pers/hd/d/Doerr:Carola")
    soup = BeautifulSoup(r.content,"html.parser")
    soup2 = BeautifulSoup(r1.content,"html.parser")
    #header = soup.find_all('div',attrs={'id':'coauthor-section'})
    body= soup.find_all('div',attrs={'class':'person'})
    body2 = soup2.find_all('div',attrs={'class':'person'})
    for i,j in zip(body,body2):
        i=i.string
        j=j.string
        if i is None or j is None :
            continue
        i=i.split()
        j=j.split()
        nom=i[1]+" "+i[0]
        name = j[1] + " "+ j[0]
        tab2.append(nom)
        tab3.append(name)
    for i,j in zip(tab2,tab3):
        if j in tab:
            print (j)
            print('okay')
        if i in tab:
            print (i)
            print('okay')


   # P = G.plot()
    #P.show()



"""------------------------------------------------Question 2 -------------------------------------"""
@route("/authors/<nom>/<prenom>")
def author(nom,prenom):
    journal =  getAllInfo()
    coAuteur = getAllInfoCoAuteur(nom,prenom)
    conf = getAllInfoConf()
    return template('fiche_auteur.tpl', nom=nom, prenom=prenom, x=(len(journal)-1),y=(len(conf)-1),z=(len(coAuteur)-1) )
    
            

run(bottle.app(), host='localhost', port=8800, debug= True)
