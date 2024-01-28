from fastapi import FastAPI, Body
from fastapi import Path    # nos ayuda a validar parametros de RUTA
from fastapi import Query    # nos ayuda a validar parametros de QUERY
from fastapi.responses import HTMLResponse  # envia contenido en formato HTML hacia el cleinte
from fastapi.responses import JSONResponse  # envia contenido en formato JSON hacia el cleinte
from pydantic import BaseModel      # nos ayuda a crear el esquema de datos
from pydantic import Field      # nos ayuda a crear validaciones en los datos que manipulamos
from typing import Optional
from typing import List     # nos ayuda a definir el tipo de elmento que devolvemos
from jwt_manager import create_token
from jwt_manager import validate_token
from fastapi.security import HTTPBearer
from fastapi import Request
from fastapi import HTTPException
from fastapi import Depends

#---------------------------------------------------------------------------------------
# UVICONR
# para iniciar la aplicacion utilizamos "uvicorn" con el comando:
# uvicorn main:app --reload --port 5000 --host 0.0.0.0
# | --reload : cuandod etecta cambios en el archivo de la app recarga
# | --port : defini el puerto donde escucha
# | --hots : definimos que este disponible para todos los dispositivos de la red
#----------------------------------------------------------------------------------------

app = FastAPI()        # instacio un elemento, con el nombre de la aplicacion
app.title = "Mi app con FastAPI"
app.version = '0.0.1'

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != 'admin@gmail.com':
            raise HTTPException(status_code=403, detail='Credenciales invalidas')

# Creamos un modelo que nos permita cargar info del usuario
class User(BaseModel):
    email:str
    password:str

# Esquema de Datos de cada pelicula, creamos una clase con la ayuda de BaseModel
class Movie(BaseModel):
    #id: int | None = None   # valor, tipos de datos aceptados, y el valor por defecto
    id: Optional[int] = None
    #title: str = Field(default='Una Peli', min_length=5, max_length=15)   # definimos con Field el validador de 15 digitos maximos
    #overview: str = Field(default='Alguna descripcion', min_length=15, max_length=50)
    #year: int = Field(default=2022, le=2022)
    title: str = Field(min_length=5, max_length=15)   # definimos con Field el validador de 15 digitos maximos
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2022)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    class Config:   # con esto quitamos los valores por defecto del Field
        json_schema_extra = {
            'example': {
                'id': 1,
                'title': 'Otra Peli',
                'overview': 'otra descripcion',
                'year': 2009,
                'rating': 7.7,
                'category': 'Default'
            }
        }


movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'    
    },
    {
        'id': 2,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'    
    }
]

movies_filter = []


@app.get('/', tags=['home'])           # definimos el endpoint, dentro de los () definimos la reuta de incio
def message():
    return HTMLResponse('<h1>Hello word</h1>')

@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == 'admin@gmail.com' and user.password == 'admin':
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content=token)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    #return movies
    return JSONResponse(status_code=200, content=movies)

@app.get('/movies/{id}', tags=['movies'], response_model=Movie)   #en la ruta definimos parametros de entrada entre {}
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:   # con "Path" realizamos la validacion de los parametros
    for item in movies:
        if item['id'] == id:
            #return item
            return JSONResponse(content=item)
    return JSONResponse(status_code=404, content=[])
    #return movies[id - 1]

# parametro tipo query
@app.get('/movies/', tags=['movies'], response_model=List[Movie])        #cuando defino un parametro en la funcione solamente, no en la ruta automaticamente FatAPI lo toma como parametro query
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:  # con "Query" realizamos la validad de los parametros de este tipo
    #for item in movies:
    #    if item['category'] == category:
    #        movies_filter.append(item)
    #        return item
    data = [item for item in movies if item['category'] == category]
    #return []
    return JSONResponse(content=data)
    #return movies_filter

@app.post('/movies', tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    # utilizamos la clase esquema para no tener que escribir todos los atributos esperados
    movies.append(movie.dict())
    #return movies
    return JSONResponse(status_code=201, content={'message': 'Se ha registrado la pelicula'})

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview']= movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
    #return movies
    return JSONResponse(status_code=200, content={'message': 'Se ha modificado la pelicula'})


@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int) -> dict:
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
    #return movies
    return JSONResponse(status_code=200, content={'message': 'Se ha eliminado la pelicula'})
