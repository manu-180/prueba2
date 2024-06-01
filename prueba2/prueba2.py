import reflex as rx
import firebase_admin
from firebase_admin import credentials, db
import os
import dotenv
import asyncio
from datetime import time

# Función para verificar periódicamente la base de datos
async def check_database_periodically():
    while True:
        firebase = FireBase()
        data = firebase.data()
        rx.State.update_forward_refs()  # Forzar la actualización del estado para re-renderizar los componentes
        await asyncio.sleep(10)  # Espera 10 segundos antes de volver a verificar

# Clase para manejar la lógica de Firebase
class Horarios(rx.Base):
    id: int
    horario: time
    cant_users: int

dotenv.load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

firebase_sdk = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(firebase_sdk, {"databaseURL": DATABASE_URL})

class FireBase():
    ref = db.reference("/Horarios")

    def data(self):
        data = self.ref.get("-NzBFPwsONhMP5SKqs9u")
        dict_data = data[0]
        class_data = []

        for clave, valor in dict_data.items():
            horario_parts = [int(part) for part in valor["horario"].split(":")]
            class_data.append(Horarios(
                id=valor["id"],
                horario=time(horario_parts[0], horario_parts[1]),
                cant_users=valor["cant_users"]
            ))
        return class_data

    def horarios(self):
        horarios = []
        for i in self.data():
            horarios.append(i.horario)
        return horarios

    def unico_horario(self, id):
        for i in self.data():
            if i.id == id:
                return i.horario

    def cant_users(self, id) -> int:
        for i in self.data():
            if i.id == id:
                return i.cant_users

    def check_cant_users(self, id):
        return self.cant_users(id) < 4

    def reservar(self, id):
        data = self.ref.get("-NzBFPwsONhMP5SKqs9u")
        dict_data = data[0]
        for clave, valor in dict_data.items():
            if valor["id"] == id:
                usuarios = self.ref.child(clave)
                contador = valor["cant_users"]
                if contador < 4:
                    usuarios.update({"cant_users": contador + 1})
                else:
                    print("La clase está llena")

    def cancelar(self, id):
        data = self.ref.get("-NzBFPwsONhMP5SKqs9u")
        dict_data = data[0]
        for clave, valor in dict_data.items():
            if valor["id"] == id:
                usuarios = self.ref.child(clave)
                contador = valor["cant_users"]
                if contador > 0:
                    usuarios.update({"cant_users": contador - 1})

firebase = FireBase()

class ReservaCancela(rx.State):
    
    async def reservar_turno(self, id: int) -> list:
        reservar_la_clase = firebase.reservar(id)
        return reservar_la_clase


    async def cancelar_turno(id: int):
        cancelar_la_clase = firebase.cancelar(id)
        return cancelar_la_clase

    async def data():
        data = await data()
        print(data)
        return data
    
ReservaCancela.reservar_turno(3)

async def data():
    return firebase.data()

class Color():
    color_red: str = "red"
    color_green: str = "green"

color = Color()

@rx.page(
    title="turnos",
    description="Taller de cerámica",
    on_load=ReservaCancela.data
)
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

def button_green(text, id) -> rx.Component:
    return rx.button(
        rx.text(text),
        on_click=ReservaCancela.reservar_turno(id),
        color_scheme=color.color_green
    )

def button_red(text, id) -> rx.Component:
    return rx.center(
        rx.button(
            rx.text(text),
            disabled=True,
        ),
        rx.button(
            rx.text("¿Cancelar esta clase?"),
            on_click=ReservaCancela.cancelar_turno(id)
        ),
        rx.vstack(
            rx.text("(Si no cancelas con un día de anticipación",
                    size="1",
                    spacing="0px",
                    padding="0px",
                    margin="0px"),
            rx.text("no podrás recuperar la clase)",
                    size="1",
                    spacing="0px",
                    padding="0px",
                    margin="0px"
            )
        )
    )

def button(id):
    return rx.cond(
        firebase.check_cant_users(id),
        button_green(f"Turno de las {firebase.unico_horario(id)}", id),
        button_red(f"Turno de las {firebase.unico_horario(id)}", id)
    )

app = rx.App()
app.add_page(index)

async def main():
    # Iniciar la tarea de verificación periódica de la base de datos
    asyncio.create_task(check_database_periodically())
    app._compile()

if __name__ == "__main__":
    asyncio.run(main())
