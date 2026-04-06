>[!WARNING]
>**<span style="color:red">Este programa genera un fichero que TIENES QUE VERIFICAR, porque puede ser que aun tiene errores, por ejemplo:</span>**
>* Hay varias maneras de codificar los acentos, que no son todas compatibles.
>* Puede aparecer dos veces el mismo articulo en la lista de citas: uno de ArXiv, otro de la revista "real". Hay que quitar el ArXiv...
>* Puede ser que autores se esconden bajo "et al." y que el sistema no clasifique bien.
>
>**<span style="color:red">¡NO GARANTIA AT ALL DE QUE EL RESULTADO SEA TOTALMENTE CORRECTO!</span>**

### Installation

Este programa requiere python >= 3.8.


**pip install -U git+https://github.com/Morisset/SNI_ads.git**

Este programa esta hecho para generar un documento ayudando a rellenar el Perfil Unico de RIZOMA que SECIHTI usa para los investigadores que renovan o entran en el SNI. En particular se requiere poner los articulos publicados con citas de tipo A y B:


* _Tipo A: Aquellas realizadas en productos de investigación firmadas por uno o varios autores, entre los cuales no se encuentra ninguno que sea autor del trabajo al que hace referencia en la cita. Es decir, se deben excluir las auto citas de todos los autores._
* _Tipo B: Aquellas realizadas en productos de investigación firmadas por uno o varios autores, entre los cuales puede encontrarse uno o varios autores del trabajo al que se hace referencia en la cita, pero no el investigador evaluado. Es decir, se deben excluir únicamente las autocitas del autor seleccionado._

_Se  sugiere  realizar  la  búsqueda de  las  citas a  través  de  alguna  de  las  bases  de  datos internacionales especializadas._

El programa da tambien el DOI y la liga hacia ADS que hay que incluir : _"Escriba el enlace que permita confirmar el número de citas reportado."_


Agregué citas de tipo "C", que son aquellas donde el autor mismo se autocita. No es un requisito de SECIHTI

Se usa ADS para buscar la información requirida. El primer problema a arreglar es el filtro de ADS que impidó hacer multiples busquedas en sequido (para evitar que los robotes que poblan el WWW se pongan a chupar todos los articulos...). Para evitar este problema, hay que registrarse a la pagina: https://ui.adsabs.harvard.edu/#user/account/register
Una ves registrado, uno puede pedir un "token", o sea un clave que se requiere para tener acceso a la base ADS.

Se hace por aca:
https://ui.adsabs.harvard.edu/#user/settings/token
Hay que recuperar una clave de este tipo: "5K123456789HCzvJWn7312345678987M"

### Usage

SNIads [-h] [-t TOKEN] [-m MAX_PAPERS] [-oc] [-sy START_YEAR] [-ns] [-nf] [-ex EXCLUDE_BIBCODES] [-in INCLUDE_BIBCODES] [-r ROWS] [-v] [-V] author

positional arguments: 
* author : Author to search for.

options:
*  -h, --help:           show this help message and exit
*  -t TOKEN, --token TOKEN: ADS token. It can also be stored in ADS_DEV_KEY environment variable.
*  -m MAX_PAPERS, --max_papers MAX_PAPERS: Maximum number of papers to consider.
*  -oc, --only_cited:     Only cited papers are printed.
*  -sy START_YEAR, --start_year START_YEAR: Only papers published from this year onwards are considered.
*  -ns, --no_screen:      No screen output.
*  -nf, --no_file:        No file output.
*  -ex EXCLUDE_BIBCODES, --exclude_bibcodes EXCLUDE_BIBCODES:  A filename containing the bibcodes to be excluded
*  -in INCLUDE_BIBCODES, --include_bibcodes INCLUDE_BIBCODES: A filename containing the bibcodes to be included. In this case, the author may be omitted
*  -r ROWS, --rows ROWS:  Number of ADS results per page (default 200).
*  -v, --verbose:         Verbose
*  -V, --version:         Display version information and exit.


### Ejemplo

`SNIads 'Morisset, Christophe' -t "5K123456789HCzvJWn7312345678987M"` -sy 2021

donde se da el nombre del author (mejor poner en nombre y el apelido) que buscas, el token que has recuperado del sitio ADS (el que esta en este ejemplo NO funciona), y se pide considerar solamente los articulos desde 2021.

Deberia resultar en un fichero LaTex de nombre en este caso "refs_MorissetChristophe.tex" , de lo cual se genera un PDF bonito. Usarlo para rellenar los campos de los articulos en el "Perfil Unico".
Mejor guardar este fichero en caso de que piden justificación de los numeros. 

Si tienes un nombre bastane comun pero que tienes ya una lista de los bibcodes que coresponden a tus articulos en un fichero por ejemplo nombrado in_refs.dat de este tipo - no importa si hay [] o () - :
```
2022A&A...668A..74M
2022NatAs...6.1421D
2022A&A...667A..35R
(2022MNRAS.512.3436E)
2022MNRAS.512.4003M
[2022MNRAS.512.2202A]
2022MNRAS.511....1S
```

puedes usar:

`SNIads  -t "5K123456789HCzvJWn7312345678987M" -in in_refs.dat "Morisset, C."` 

Si se debe mencionar un autor, para que se puede separar las citas de tipo B y C.

Una lista de bibcodes se puede generar de manera facil desde ADS (Export/Other Formats/Custom Format) usando el formato %R.

### From a python script

The following is used if you want to have access to the intermediate results. It runs in a python scipt or a python interactive session.

```
from SNIads import SNIads
token = "5KAUJBW123456789dHCzvJWn73WyKVvNvyugC87M" # this one is fake, you need to use your own token
token=None # use this is you defined the token using the ADS_DEV_KEY environment variable
author = 'Morisset, C.'             
articulos = SNIads.get_papers(author, token=token)
citas = SNIads.get_citations(articulos, token=token)
SNIads.print_results(author, articulos, citas)
with open('refs_{}.tex'.format(SNIads.clean_author(author)), 'w') as f:
    SNIads.print_results(author, articulos, citas, f)
```
