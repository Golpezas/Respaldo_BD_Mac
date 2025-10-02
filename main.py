import os
from config import SPREADSHEET_ID, LOCAL_ROOT_FOLDER, PHOTO_HEADERS
from src.drive_service import DriveService
from src.data_processor import DataProcessor

def main():
    """Función principal para orquestar el proceso de descarga y actualización."""
    print("Iniciando el proceso de descarga y normalización de datos...")

    # Crear el directorio LOCAL_ROOT_FOLDER antes de exportar
    try:
        os.makedirs(LOCAL_ROOT_FOLDER, exist_ok=True)
        print(f"Directorio creado o verificado: {LOCAL_ROOT_FOLDER}")
    except Exception as e:
        print(f"Error al crear el directorio {LOCAL_ROOT_FOLDER}: {e}")
        return

    try:
        drive_service = DriveService()
    except Exception as e:
        print(f"Error al autenticar con Google Drive: {e}")
        return

    spreadsheet_local_path = os.path.join(LOCAL_ROOT_FOLDER, "Formulario_Unificado.xlsx")
    try:
        if not drive_service.export_spreadsheet(SPREADSHEET_ID, spreadsheet_local_path):
            print("No se pudo exportar la hoja de cálculo. Saliendo.")
            return
    except Exception as e:
        print(f"Error al exportar la hoja de cálculo a {spreadsheet_local_path}: {e}")
        return

    data_processor = DataProcessor(drive_service, LOCAL_ROOT_FOLDER, PHOTO_HEADERS)
    data_processor.process_data(spreadsheet_local_path)
    
    print("\nProceso de automatización finalizado con éxito. ¡Listo para usar los datos localmente! 🎉")

if __name__ == "__main__":
    main()