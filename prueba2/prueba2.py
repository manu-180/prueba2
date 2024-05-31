import reflex as rx
import firebase_admin
from firebase_admin import credentials, db
import os
import dotenv
# import asyncio

# # Función para verificar periódicamente la base de datos
# async def check_database_periodically():
#     while True:
#         # Consulta la base de datos y verifica los cambios
#         # Si hay cambios, actualiza dinámicamente la página
#         await asyncio.sleep(10)  # Espera 10 segundos antes de volver a verificar

# # Función para manejar los cambios en la base de datos
# # Función para manejar los cambios en la base de datos
# async def handle_database_changes():
#     while True:
#         # Verifica si hay cambios relevantes en la base de datos
#         # Por ejemplo, verifica si algún horario ha alcanzado el límite de usuarios
#         for horario in firebase.data():
#             if horario.cant_users >= 4:
#                 # Si un horario ha alcanzado el límite de usuarios, actualiza dinámicamente la página
#                 index.update()

#         # Espera un tiempo antes de volver a verificar
#         await asyncio.sleep(10)  # Espera 10 segundos antes de volver a verificar



class Horarios(rx.Base):
    id = int
    horario = int
    cant_users = int

dotenv.load_dotenv()
    
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

firebase_sdk = credentials.Certificate(f"C:\\Users\\Manuel\\Desktop\\Folder\\prueba2\\{GOOGLE_APPLICATION_CREDENTIALS}")
firebase_admin.initialize_app(firebase_sdk, {"databaseURL": DATABASE_URL})

class FireBase():
    ref = db.reference("/Horarios")

    def data(self):
        data = list(self.ref.get("-NzBFPwsONhMP5SKqs9u"))
        dict_data = data[0]

        class_data = []

        for clave, valor in dict_data.items():
            class_data.append(Horarios(id=valor["id"], horario=valor["horario"], cant_users=valor["cant_users"]))
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
                    usuarios.update({"cant_users": contador})
                else:
                    print("la clase esta llena")

    def cancelar(self, id):
        data = list(self.ref.get("-NzBFPwsONhMP5SKqs9u"))
        dict_data = data[0]
        for clave, valor in dict_data.items():
            if valor["id"] == id:
                usuarios = self.ref.child(clave)
                contador = valor["cant_users"]
                contador -= 1
                if contador >= 0:
                    usuarios.update({"cant_users": contador})

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
    return rx.center(
        rx.button(
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
    return rx.cond(
        firebase.check_cant_users(id),
        button_green(f"Turno de las {firebase.unico_horario(id)}", Reserva_cancela.reservar_turno(id), id),
        button_red(f"Turno de las {firebase.unico_horario(id)}", id)
    )

app = rx.App()
app.add_page(index)

# asyncio.create_task(check_database_periodically())
# asyncio.create_task(handle_database_changes())

if __name__ == "__main__":
    app.run()