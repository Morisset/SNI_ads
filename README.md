**WARNING: este programa genera un fichero que TIENES QUE VERIFICAR, porque puede ser que aun tiene errores, por ejemplo:**
* hay varias maneras de codificar los acentos, que no son todas compatibles.
* puede aparecer dos veces el mismo articulo en la lista de citas: uno de ArXiv, otro de la revista "real". Hay que quitar el ArXiv...

**UPDATE: Versión 5.x es mucho mas eficiente y no deberia tener problemas con el limite de numero de conexiones. Pero se requiere ads version 0.11.3 (30 dec. 2015), tienes que hacer el update si no es el caso.**

Este programa esta hecho para generar el documento que CONACyT pide para los investigadores que renovan o entran en el SNI. En particular lo siguiente:

_" En la Sección Citas de Artículos adjunte un archivo en formato PDF no mayor a  2MB, que  contenga  la  relación  de  las  citas  externas  globales  a  su  obra, separando las citas por:_
* _Tipo A: Aquellas realizadas en productos de investigación firmadas por uno o  varios  autores  dentro  de  los  cuales  no  hay  ninguno  que  sea  autor  del trabajo referido a la cita._
* _Tipo B: Aquellas realizadas en productos de investigación firmadas por uno o varios autores dentro de los cuales puede haber uno o varios autores del  trabajo referido en la cita pero no el investigador mismo._

_Se  sugiere  realizar  la  búsqueda de  las  citas a  través  de  alguna  de  las  bases  de  datos internacionales especializadas."_

Se usa ADS para buscar la información requirida. Elprimer problema a arreglar es el filtro de ADS que impidé hacer multiples busquedas en sequido (para evitar que los robotes que poblan el WWW se pongan a chupar todos los articulos...). Para evitar este problema, hay que registrarse a la pagina: https://ui.adsabs.harvard.edu/#user/account/register
Una ves registrado, uno puede pedir un "token", o sea un clave que se requiere para tener acceso a la base ADS.

Se hace por aca:
https://ui.adsabs.harvard.edu/#user/settings/token
. Hay que recuperar una clave de este tipo:
"5K123456789HCzvJWn7312345678987M"

Otro paso antes de correr el programa es la instalación de la librarya python "ads". Se requiere la mas reciente versión (0.11.3, del 30 de dic. de 2015).
Supongo que tienen una distribución de python en buen estado, con el programa de manejo de paquetes. En este caso, solo hacer (para instalar o hacer el update):

`pip install -U ads`

Puede ser que necesiten tambien unidecode (si ya lo tienen, lo siguiente no va hacer daños):

`pip install unidecode`

Et voilà!

Ya pueden descargar el programa que hice desde aca: https://github.com/Morisset/SNI_ads/raw/master/SNI_ads.py

NEW in version 4.x: Hay que guardarlo donde quieren, cambiar los derechos para que sea un ejecutable (chmod a+x SNI_ads.py) y ejecutar desde el directorio donde esta guardado:

`SNI_ads.py 'Morisset, Christophe' -t "5K123456789HCzvJWn7312345678987M"`

donde se da el nombre del author (mejor poner en nombre y el apelido) que buscas y el token que has recuperado del sitio ADS (el que esta en este ejemplo NO funciona).

Si tienes un nombre bastane comun pero que tienes ya una lista de los bibcodes que coresponden a tus articulos en un fichero por ejemplo nombrado in_refs.dat de este tipo (puede ser que los [] sean (), no importa):
```
[2016A&A...585A..69G] 

[2015EAS....71..313G] 

[2015arXiv151004548M] 

[2015MNRAS.452.2606G] 

[2015MNRAS.452.1764R] 

[2015IAUGA..2255587P] 
```

puedes usar:

`SNI_ads.py  -t "5K123456789HCzvJWn7312345678987M" -in in_refs.dat` 

Deberia resultar en un fichero LaTex de nombre en este caso "refs_MorissetChristophe.tex" , de lo cual se genera un PDF bonito. 

