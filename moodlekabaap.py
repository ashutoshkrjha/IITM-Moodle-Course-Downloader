import cookielib
import urllib
import urllib2
from bs4 import BeautifulSoup
import os.path
import os
import filecmp
import sys

global i
global directory

def save_file( data, filename ) :
    global i
    global directory
    
    if os.name == 'posix':
        filename = directory + "/" + filename
        tempfile = directory + "/temp"
    else :
        filename = directory + "\\" + filename
        tempfile = directory + "\\temp"

    filename = urllib.unquote( filename )    
    if not os.path.exists( directory ) :
        os.makedirs( directory )

    with open( tempfile, "wb" ) as code :
        code.write( data )     
    if os.path.isfile( filename ) :
        if filecmp.cmp( filename, tempfile ) == True :
            os.remove( tempfile )
        else :
            name_split = filename.split('.')
            filename = name_split[0] + str(i) + "." + name_split[-1]
            if os.path.isfile( filename ) :
                if filecmp.cmp( filename, tempfile ) == True :
                    os.remove( tempfile )
            else:
                os.rename( tempfile, filename )
            i += 1
    else:
        os.rename( tempfile, filename )
        
def embedded_file( link ) :
    filename = link.split('/')[-1]
    data = urllib2.urlopen( link ).read()
    save_file( data, filename )

def direct_download( data ):
    filename = data.info()['Content-Disposition'] . split( '=' )[-1] . strip( '"' )
    save_file( data.read(), filename )

def auth( username, password ):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ) )
    urllib2.install_opener( opener )
    authentication_url = 'https://courses.iitm.ac.in/login/index.php'
    payload = {
      'username' : username,
      'password' : password
      }
    data = urllib.urlencode( payload )
    req = urllib2.Request( authentication_url, data )
    return req

#Change here the Course Numbers and the year you want

if __name__ == "__main__":
    allsub = ["AM2200" ,"BT1010" , "CS2100", "EE1100", "HS3410" , "ID1200" , "MA2130"  , "ME2050"]
    year = "2015"

#Change here with your LDAP Username and Password

    username = "PUT_USERNAME_HERE"
    password = "PUT_PASSWORD_HERE"

    os.chdir(os.path.dirname(os.path.abspath((sys.argv[0]))))
    
    req = auth( username, password )
    resp = urllib2.urlopen( req )
    soup = BeautifulSoup( resp.read() )
    
    for link in soup.find_all( 'a' ) :
        for subject in allsub :
            if subject in str( link ) and year in str( link )  :
                sub_link = link.get( 'href' )
                print "Downloading " + subject
                directory = subject + "-" + year
                resp = urllib2.urlopen( sub_link )
                soup = BeautifulSoup( resp.read() )
                alldocs = list( set( soup.find_all('a') ) )
                
                total = 0
                i = 0

                for doc in alldocs :
                    if 'mod/resource' in doc.get( 'href' ):
                        total += 1

                        doc_click = urllib2.urlopen( doc.get( 'href' ) )

                        if 'Content-Disposition' in str( doc_click.info() ) :
                            direct_download( doc_click )
                        
                        else :
                            soup1 = BeautifulSoup( doc_click.read() )
                            page_links = soup1.find_all( 'a' )
                            page_images = soup1.findAll( 'img' )
                            for img in page_images :
                                img_links = img.get( 'src' )
                                if '.jpeg' in str( img_links ).lower() or '.jpg' in str( img_links ).lower() :
                                    embedded_file( img_links )
                            for links in page_links :
                                doc_links = links.get( 'href' )
                                if 'pdf' in str( doc_links ).lower() or 'doc' in str( doc_links ).lower():
                                    embedded_file( doc_links )

                    elif 'mod/folder' in doc.get('href') :
                        doc_click = urllib2.urlopen( doc.get ( 'href' ) )
                        soup1 = BeautifulSoup( doc_click.read() )
                        page_links = soup1.find_all( 'a' )
                        for link in page_links:
                            if 'download' in link.get( 'href' ):
                                total += 1
                                link_click = urllib2.urlopen( link.get( 'href' ) )
                                if 'Content-Disposition' in str( link_click.info() ) :
                                    direct_download( link_click )
                                        
                if os.path.exists( directory ) and len( os.listdir( directory ) ) != total:
                   print subject + ": Go to moodle and check if some files not downloaded" 
                else:
                    print subject+": done"
