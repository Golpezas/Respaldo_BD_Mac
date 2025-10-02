import os
import re
import pandas as pd
from urllib.parse import urlparse
from config import OUTPUT_BASE_FILENAME, TARGET_MONTH, TARGET_YEAR, DATE_COLUMN

class DataProcessor:
    def __init__(self, drive_service, local_root_folder, photo_headers):
        self.drive_service = drive_service
        self.local_root_folder = local_root_folder
        self.photo_headers = photo_headers
        os.makedirs(self.local_root_folder, exist_ok=True)
        # Crear subcarpetas para cada tipo de foto dentro de local_root_folder
        for header in self.photo_headers:
            folder_name = self._sanitize_folder_name(header)
            os.makedirs(os.path.join(self.local_root_folder, folder_name), exist_ok=True)

    def _sanitize_folder_name(self, name):
        return re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().replace(' ', '_')

    def _get_file_id_from_url(self, url):
        """Extrae el ID del archivo de Google Drive desde la URL."""
        if not url or not isinstance(url, str):
            return None
        parsed_url = urlparse(url)
        file_id = None
        path_parts = parsed_url.path.split('/')
        if 'd' in path_parts:
            try:
                file_id = path_parts[path_parts.index('d') + 1]
                return file_id
            except IndexError:
                pass
        query_parts = parsed_url.query.split('&')
        for part in query_parts:
            if part.startswith('id='):
                file_id = part.split('id=')[1]
                return file_id
        return None

    def _get_unique_output_path(self, base_path, base_name):
        """Genera un nombre de archivo único añadiendo un número si el archivo ya existe."""
        counter = 1
        output_path = os.path.join(base_path, f"{base_name}.xlsx")
        while os.path.exists(output_path):
            counter += 1
            output_path = os.path.join(base_path, f"{base_name}{counter}.xlsx")
        return output_path

    def process_data(self, spreadsheet_path):
        try:
            df = pd.read_excel(spreadsheet_path)
        except Exception as e:
            print(f"Error al leer el archivo Excel: {e}")
            return False

        # --- LÓGICA DE FILTRADO POR MES/AÑO ---
        df_filtered = df.copy()
        if DATE_COLUMN in df.columns:
            try:
                # 1. Convertir la columna de fecha al tipo datetime
                df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors='coerce')
                
                # 2. Filtrar filas para el mes y año objetivo
                df_filtered = df[
                    (df[DATE_COLUMN].dt.month == TARGET_MONTH) &
                    (df[DATE_COLUMN].dt.year == TARGET_YEAR)
                ].copy()
                
                if df_filtered.empty:
                    print(f"No se encontraron datos para {TARGET_MONTH}/{TARGET_YEAR}. Proceso finalizado (sin error).")
                    return True 
                
                print(f"Filtrando: Se procesarán {len(df_filtered)} filas para {TARGET_MONTH}/{TARGET_YEAR}.")
            except Exception as e:
                print(f"Advertencia: Error al filtrar por fecha ({e}). Procesando todos los datos.")
                df_filtered = df.copy()
        else:
            print(f"Advertencia: Columna de fecha '{DATE_COLUMN}' no encontrada. Procesando todos los datos.")
            
        updated_df = df_filtered.copy()
        # --- FIN LÓGICA DE FILTRADO ---

        for index, row in df_filtered.iterrows():
            print(f"Procesando fila {index + 2}...")
            for header in self.photo_headers:
                if header in row and pd.notna(row[header]): # Usa pd.notna para manejar NaNs de forma segura
                    url = row[header]
                    file_id = self._get_file_id_from_url(url)
                    if file_id:
                        folder_name = self._sanitize_folder_name(header)
                        # Intenta usar 'ID de Relevamiento' o usa un índice genérico
                        relevamiento_id = row.get("ID de Relevamiento", f"row_{index + 2}")
                        local_file_name = f"{relevamiento_id}_{file_id}.jpg"
                        local_path = os.path.join(self.local_root_folder, folder_name, local_file_name)
                        
                        # Verifica si el archivo ya existe localmente para evitar descargas repetidas
                        if not os.path.exists(local_path):
                            if self.drive_service.download_file(file_id, local_path):
                                updated_df.at[index, header] = local_path
                            else:
                                print(f"Manteniendo enlace original para la fila {index + 2}, columna '{header}'.")
                        else:
                            updated_df.at[index, header] = local_path
                            # print(f"Archivo ya existente en: {local_path}. Saltando descarga.")
                    else:
                        # Si no se encuentra el ID, mantiene el valor original (la URL)
                        pass
        
        output_path = self._get_unique_output_path(self.local_root_folder, OUTPUT_BASE_FILENAME)
        try:
            updated_df.to_excel(output_path, index=False)
            print(f"\nProceso finalizado. Archivo actualizado guardado en: {output_path}")
            return True
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            return False