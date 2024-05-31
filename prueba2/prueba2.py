import reflex as rx
import firebase_admin
from firebase_admin import credentials, db

class Horarios(rx.Base):
    id = int
    horario = int
    cant_users = int


firebase_sdk = credentials.Certificate("C:\\Users\\Manuel\\Desktop\\Folder\\prueba2\\taller-f75e9-firebase-adminsdk-6su0y-b407a5dc0d.json")

firebase_admin.initialize_app(firebase_sdk, {"databaseURL": "https://taller-f75e9-default-rtdb.firebaseio.com/"})

# ref.push({"id": 1, "horario": "12:00", "cant_users": 0})
# ref.push({"id": 2, "horario": "14:00", "cant_users": 0})
# ref.push({"id": 3, "horario": "16:00", "cant_users": 0})
# ref.push({"id": 4, "horario": "18:00", "cant_users": 0})
# ref.push({"id": 5, "horario": "20:00", "cant_users": 0})
class FireBase():
    ref = db.reference("/Horarios")

    def data(self):
        data = list(self.ref.get("-NzBFPwsONhMP5SKqs9u"))
        dict_data = data[0]
        
        class_data=[]

        for clave, valor in dict_data.items():
            class_data.append(Horarios(id=valor["id"], horario = valor["horario"], cant_users= valor["cant_users"]))
        return class_data
    
    def horarios(self):    
        horarios=[]
        for i in self.data():
            horarios.append(i.horario)
        return horarios
    
    def unico_horario(self, id):
        for i in self.data():
            if i.id == id:
                return i.horario
            
    def cant_users(self, id) -> list:
        for i in self.data():
            if i.id == id:
               return i.cant_users
           
    def check_cant_users(self, id):
        if self.cant_users(id) < 4:
            return True
        return False
    
    def reservar(self, id):
        data = list(self.ref.get("-NzBFPwsONhMP5SKqs9u"))
        dict_data = data[0]
        for clave, valor in dict_data.items():
            if valor["id"] == id:
                usuarios = self.ref.child(clave)
                contador = valor["cant_users"]
                contador += 1
                if contador <= 4:
                    usuarios.update({"cant_users":contador})
                else: print("la clase esta llena")
    
    def cancelar(self, id):
        data = list(self.ref.get("-NzBFPwsONhMP5SKqs9u"))
        dict_data = data[0]
        for clave, valor in dict_data.items():
            if valor["id"] == id:
                usuarios = self.ref.child(clave)
                contador = valor["cant_users"]
                contador -= 1
                if contador >= 0:
                    usuarios.update({"cant_users":contador})
        
                
        

firebase = FireBase()


class Reserva_cancela(rx.State):
    async def reservar_turno(self, id: int) -> list:
        reservar_la_clase = firebase.reservar(id)
        return reservar_la_clase
    
    async def cancelar_turno(self, id: int) -> list:
        cancelar_turno = firebase.cancelar(id)
        return cancelar_turno
    
    async def data(self):
        self.data_info = await data()
        print(self.data_info)
    

async def data():
    return firebase.data()
        


class Color():
    color_red: str = "red"
    color_green: str = "green"

color = Color()

@rx.page(
    title="turnos",
    description="Taller de cerámica",
    on_load=Reserva_cancela.data)
def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            button(1),
            button(2),
            button(3),
            button(4),
            button(5)
        )
    )

def button_green(text, click, id) -> rx.Component:
    return rx.button(
        rx.text(text),
        on_click=click,
        color_scheme=color.color_green
    )



def button_red(text, id) -> rx.Component:
    return rx.center(rx.button(
        rx.text(text),
        disabled=True,
    ),
    rx.button(
        rx.text("¿Cancelar esta clase?"),
        on_click=Reserva_cancela.cancelar_turno(id)
        ),
    rx.vstack(
        rx.text("(Si no cancelas con un dia de anticipacion",
            size="1",
            spacing="0px",
            padding="0px",
            margin="0px"),
        rx.text("no podras recuperar la clase)",
                size="1",
                spacing="0px",
                padding="0px",
                margin="0px"
            )
        )
    )


def button(id):
    return rx.cond(firebase.check_cant_users(id),
                   button_green(f"Turno de las {firebase.unico_horario(id)}", Reserva_cancela.reservar_turno(id), id),
                   button_red(f"Turno de las {firebase.unico_horario(id)}", id)

                )  
    
app = rx.App()
app.add_page(index)