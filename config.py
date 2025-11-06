import os
import datetime

# --- CONFIGURACIÓN DE GOOGLE DRIVE ---
SPREADSHEET_ID = "1aAgfrKVw8TOSu1LBIaSqWoG3DAC0wxYVmJyHpkxNARw"

# Columna que contiene la fecha de relevamiento en tu hoja de cálculo
DATE_COLUMN = "Marca temporal" # AJUSTA ESTO SI EL NOMBRE DE LA COLUMNA ES DIFERENTE

# --- CONFIGURACIÓN DE RESPALDO POR MES ---
# Define el mes y año que deseas respaldar.
# Por ejemplo, para respaldar Septiembre de 2025:
TARGET_MONTH = 11 
TARGET_YEAR = 2025

# --- CONFIGURACIÓN DE RUTAS LOCALES ---
# La ruta base donde se guardarán los directorios de respaldo
BASE_PATH = r"X:\Operaciones\Relevamientos\Relevamientos de Pozos y Sitios\Desarrollo_IT_BD\BD_FRelevamientos"

# Función para obtener una carpeta única
def get_unique_folder(base_path, base_name):
    """Genera un nombre de carpeta único añadiendo un número para cada ejecución."""
    folder_path = os.path.join(base_path, base_name)
    if not os.path.exists(folder_path):
        return folder_path 
    counter = 2 
    while True:
        new_folder_path = os.path.join(base_path, f"{base_name}{counter}")
        if not os.path.exists(new_folder_path):
            return new_folder_path
        counter += 1

# Base para el nombre de la carpeta y archivo de salida, incluyendo el mes/año
try:
    month_name = datetime.date(TARGET_YEAR, TARGET_MONTH, 1).strftime("%B_%Y").replace(" ", "_")
except ValueError:
    month_name = f"INVALID_DATE_{TARGET_MONTH}_{TARGET_YEAR}"
    print(f"Advertencia: Fecha inválida ({TARGET_MONTH}/{TARGET_YEAR}). Usando nombre genérico.")

LOCAL_ROOT_FOLDER_BASE = f"Reportes_Aysa_{month_name}"
LOCAL_ROOT_FOLDER = get_unique_folder(BASE_PATH, LOCAL_ROOT_FOLDER_BASE)
OUTPUT_BASE_FILENAME = f"Reportes_Aysa_{month_name}" 

# Encabezados de las columnas que contienen fotos
PHOTO_HEADERS = [
    "Foto Vandalismo Pozo", "Foto Vandalismo Sitio", "Foto Frontal Pozo",
    "Foto Adicional 1 Pozo", "Foto Adicional 2 Pozo", "Foto Adicional 3 Pozo",
    "Foto Frontal Sitio", "Foto Adicional 1 Sitio", "Foto Adicional 2 Sitio",
    "Foto Adicional 3 Sitio"
]