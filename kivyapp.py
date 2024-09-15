import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import csv
import unicodedata

# Configuración de la URL y la clave de ThingSpeak
THINGSPEAK_READ_URL = 'https://api.thingspeak.com/channels/2640401/feeds.json'
READ_API_KEY = '32CJ32GXQZIQA6WU'

# Configuración de la API de OpenWeatherMap
OPENWEATHERMAP_URL = 'http://api.openweathermap.org/data/2.5/weather'
WEATHER_API_KEY = '02ba9c47fe7eebfc5111f2d6281c5092'  # Reemplaza con tu clave API

# Establecer color de fondo de la ventana
Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Gris claro

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

class ThingSpeakApp(App):
    def build(self):
        # Configuración del layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # ScrollView para manejar el contenido largo
        scroll_view = ScrollView(size_hint=(1, 0.8))
        self.data_label = Label(
            text='Datos aparecerán aquí',
            font_size='18sp',
            color=(0, 0, 0, 1),
            size_hint_y=None,
            text_size=(Window.width - 20, None),
            halign='left',
            valign='top'
        )
        self.data_label.bind(texture_size=self.data_label.setter('size'))
        
        scroll_view.add_widget(self.data_label)
        
        # Botones para cargar los datos
        self.btn_load_thingspeak = Button(
            text='Cargar Datos de ThingSpeak',
            size_hint=(1, 0.1),
            background_color=(0, 0.5, 1, 1),  # Azul
            color=(1, 1, 1, 1),  # Blanco
            font_size='20sp'
        )
        self.btn_load_thingspeak.bind(on_press=self.load_thingspeak_data)
        
        self.btn_load_weather = Button(
            text='Cargar Datos del Clima',
            size_hint=(1, 0.1),
            background_color=(0.5, 0.8, 0, 1),  # Verde claro
            color=(1, 1, 1, 1),  # Blanco
            font_size='20sp'
        )
        self.btn_load_weather.bind(on_press=self.load_weather_data)
        
        self.btn_calculate_eto = Button(
            text='Calcular ETo',
            size_hint=(1, 0.1),
            background_color=(1, 0.5, 0, 1),  # Naranja
            color=(1, 1, 1, 1),  # Blanco
            font_size='20sp'
        )
        self.btn_calculate_eto.bind(on_press=self.calculate_eto)
        
        self.btn_save_data = Button(
            text='Guardar Datos de Campo',
            size_hint=(1, 0.1),
            background_color=(0.8, 0.8, 0.1, 1),  # Amarillo
            color=(1, 1, 1, 1),  # Blanco
            font_size='20sp'
        )
        self.btn_save_data.bind(on_press=self.show_data_inputs)
        
        self.main_layout.add_widget(scroll_view)
        self.main_layout.add_widget(self.btn_load_thingspeak)
        self.main_layout.add_widget(self.btn_load_weather)
        self.main_layout.add_widget(self.btn_calculate_eto)
        self.main_layout.add_widget(self.btn_save_data)
        
        return self.main_layout

    def load_thingspeak_data(self, instance):
        # Llamada a la función para leer datos de ThingSpeak
        try:
            params = {
                'api_key': READ_API_KEY,
                'results': 5  # Número de resultados a recuperar
            }
            response = requests.get(THINGSPEAK_READ_URL, params=params)
            response.raise_for_status()
            get_data = response.json()
            
            # Prepara los datos para mostrar
            if 'feeds' in get_data:
                feeds = get_data['feeds']
                data_text = "Datos de ThingSpeak:\n\n"
                for feed in feeds:
                    entry_id = feed.get('entry_id', 'No data')
                    created_at = feed.get('created_at', 'No data')
                    field1 = feed.get('field1', 'No data')
                    field2 = feed.get('field2', 'No data')
                    data_text += f"ID: {entry_id}, Fecha: {created_at}, Campo 1: {field1}, Campo 2: {field2}\n"
                self.data_label.text = data_text
            else:
                self.data_label.text = "Estructura JSON inesperada."
        
        except requests.RequestException as e:
            self.data_label.text = f"Error al leer los datos: {e}"
    
    def load_weather_data(self, instance):
        # Llamada a la función para leer datos del clima
        ciudad = 'Lima,PE'  # Lima, Perú
        try:
            params = {
                'q': ciudad,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(OPENWEATHERMAP_URL, params=params)
            response.raise_for_status()
            get_data = response.json()
            
            if 'main' in get_data:
                temp_max = get_data['main']['temp_max']
                temp_min = get_data['main']['temp_min']
                temp_actual = get_data['main']['temp']
                temp_promedio = (temp_max + temp_min) / 2
                
                # Guardar en archivo CSV
                self.guardar_en_csv(ciudad, temp_max, temp_min, temp_actual, temp_promedio)
                
                # Mostrar los datos en la interfaz gráfica
                data_text = f"Temperatura máxima: {temp_max}°C\n"
                data_text += f"Temperatura mínima: {temp_min}°C\n"
                data_text += f"Temperatura actual: {temp_actual}°C\n"
                data_text += f"Temperatura promedio: {temp_promedio:.2f}°C\n"
                data_text += "La información de temperatura ha sido guardada en 'temperaturas.csv'."
                
                self.data_label.text = data_text
            else:
                self.data_label.text = "Estructura JSON inesperada."
        
        except requests.RequestException as e:
            self.data_label.text = f"Error al leer los datos del clima: {e}"

    def guardar_en_csv(self, ciudad, temp_max, temp_min, temp_actual, temp_promedio, archivo='temperaturas.csv'):
        with open(archivo, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['Ciudad', 'Temperatura Máxima (°C)', 'Temperatura Mínima (°C)', 'Temperatura Actual (°C)', 'Temperatura Promedio (°C)'])
            writer.writerow([ciudad, temp_max, temp_min, temp_actual, temp_promedio])

    def calculate_eto(self, instance):
        try:
            # Leer el archivo CSV para obtener las temperaturas
            with open('temperaturas.csv', mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    temp_max = float(row['Temperatura Máxima (°C)'])
                    temp_min = float(row['Temperatura Mínima (°C)'])
                    break  # Solo necesitamos la primera fila
            
            # Imprimir los valores leídos para depuración
            print(f"Temperatura Máxima: {temp_max}°C")
            print(f"Temperatura Mínima: {temp_min}°C")

            # Calcular la temperatura promedio
            temp_promedio = (temp_max + temp_min) / 2
            
            # Imprimir la temperatura promedio para depuración
            print(f"Temperatura Promedio: {temp_promedio}°C")
            
            # Calcular ETo usando la fórmula de Hargreaves
            eto = 0.0023 * (temp_max - temp_min) ** 0.5 * (temp_promedio + 17.8)
            
            # Mostrar el resultado
            self.data_label.text += f"\nETo estimado: {eto:.2f} mm/día"
            
            # Imprimir el resultado del cálculo para depuración
            print(f"ETo Calculado: {eto:.2f} mm/día")
        
        except FileNotFoundError:
            self.data_label.text = "Archivo CSV no encontrado. Asegúrate de cargar los datos del clima primero."
        except Exception as e:
            self.data_label.text = f"Error al calcular ETo: {e}"

    def show_data_inputs(self, instance):
        # Ocultar los botones principales
        self.btn_load_thingspeak.opacity = 0
        self.btn_load_weather.opacity = 0
        self.btn_calculate_eto.opacity = 0
        self.btn_save_data.opacity = 0

        # Mostrar campos de entrada y botón de guardar
        self.area_input = TextInput(hint_text='Área del campo (hectáreas)', size_hint=(1, 0.1))
        self.water_input = TextInput(hint_text='Cantidad de agua aplicada (litros)', size_hint=(1, 0.1))
        self.main_layout.add_widget(self.area_input)
        self.main_layout.add_widget(self.water_input)

        self.btn_save = Button(
            text='Guardar Datos',
            size_hint=(1, 0.1),
            background_color=(0.1, 0.8, 0.1, 1),  # Verde
            color=(1, 1, 1, 1),  # Blanco
            font_size='20sp'
        )
        self.btn_save.bind(on_press=self.save_field_data)
        self.main_layout.add_widget(self.btn_save)

    def save_field_data(self, instance):
        # Guardar datos ingresados por el usuario en archivo CSV
        area = self.area_input.text
        water = self.water_input.text

        with open('datos_campo.csv', mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['Área (ha)', 'Agua Aplicada (L)'])
            writer.writerow([area, water])

        self.data_label.text = f"Datos guardados:\nÁrea: {area} ha\nAgua Aplicada: {water} L"

        # Restaurar los botones principales
        self.btn_load_thingspeak.opacity = 1
        self.btn_load_weather.opacity = 1
        self.btn_calculate_eto.opacity = 1
        self.btn_save_data.opacity = 1

        # Eliminar campos de entrada y botón de guardar
        self.main_layout.remove_widget(self.area_input)
        self.main_layout.remove_widget(self.water_input)
        self.main_layout.remove_widget(self.btn_save)


if __name__ == '__main__':
    ThingSpeakApp().run()
