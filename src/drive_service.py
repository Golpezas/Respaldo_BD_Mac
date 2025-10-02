import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveService:
    def __init__(self, credentials_path='credentials.json'):
        self.creds = None
        self.credentials_path = credentials_path
        self._authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    def _authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def download_file(self, file_id, file_path):
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # print(f"Descargando... {int(status.progress() * 100)}%")
            print(f"Archivo descargado: {file_path}")
            return True
        except Exception as e:
            print(f"Error al descargar archivo {file_id}: {e}")
            return False

    def export_spreadsheet(self, spreadsheet_id, file_path):
        try:
            request = self.service.files().export_media(
                fileId=spreadsheet_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_handle = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # print(f"Exportando hoja de cálculo... {int(status.progress() * 100)}%")
            print(f"Hoja de cálculo exportada a: {file_path}")
            return True
        except Exception as e:
            print(f"Error al exportar la hoja de cálculo: {e}")
            return False