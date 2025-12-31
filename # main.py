# main.py - KivyMD Android App với Backup Google Drive/Telegram
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
import json
import os
import zipfile
from datetime import datetime
import re
import requests
from plyer import filechooser

# Constants
TITLE = "SA LI GRID LIMIT"
DATA_DIR = "vehicle_data"
DB_FILE = os.path.join(DATA_DIR, "vehicle.db")

class DataManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.store = JsonStore(DB_FILE)
        self.init_data()
    
    def init_data(self):
        if not self.store.exists('config'):
            self.store.put('config', mkm='0', idate='', insdate='')
        if not self.store.exists('notes'):
            self.store.put('notes', data=[])
        if not self.store.exists('trips'):
            self.store.put('trips', data=[])
        if not self.store.exists('maintlog'):
            self.store.put('maintlog', data=[])
    
    def export_all_data(self, filename):
        """Export toàn bộ data thành JSON"""
        data = {
            'config': self.store.get('config', {}),
            'notes': self.store.get('notes', {}).get('data', []),
            'trips': self.store.get('trips', {}).get('data', []),
            'maintlog': self.store.get('maintlog', {}).get('data', []),
            'export_date': datetime.now().isoformat()
        }
        
        # Tạo ZIP backup
        zip_path = filename.replace('.json', '.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('backup.json', json.dumps(data, indent=2, ensure_ascii=False))
            zf.writestr('vehicle.db', self.store.store._storage._file.read())
        
        return zip_path
    
    def import_data(self, zip_path):
        """Import từ ZIP backup"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                if 'backup.json' in zf.namelist():
                    data = json.loads(zf.read('backup.json'))
                    # Restore data
                    for key, value in data.items():
                        if key == 'export_date':
                            continue
                        self.store.put(key, **value)
                    return True
        except:
            return False
        return False
    
    # Các method khác giữ nguyên như trước...
    def get_config(self):
        return self.store.get('config') or {}
    
    def set_config(self, key, value):
        config = self.get_config()
        config[key] = value
        self.store.put('config', **config)
    
    def get_trips(self):
        return self.store.get('trips', {}).get('data', [])
    
    def add_trip(self, trip_data):
        trips = self.get_trips()
        trip_data['id'] = len(trips) + 1
        trips.append(trip_data)
        self.store.put('trips', data=trips)
    
    def update_trip(self, trip_id, updates):
        trips = self.get_trips()
        for i, trip in enumerate(trips):
            if trip.get('id') == trip_id:
                trips[i].update(updates)
                self.store.put('trips', data=trips)
                return True
        return False
    
    def get_notes(self):
        return self.store.get('notes', {}).get('data', [])
    
    def add_note(self, note_data):
        notes = self.get_notes()
        note_data['id'] = len(notes) + 1
        notes.append(note_data)
        self.store.put('notes', data=notes)
    
    def get_maintlog(self):
        return self.store.get('maintlog', {}).get('data', [])
    
    def add_maintlog(self, log_data):
        logs = self.get_maintlog()
        log_data['id'] = len(logs) + 1
        logs.append(log_data)
        self.store.put('maintlog', data=logs)

class BackupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "backup"
        self.dm = DataManager()
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        layout.add_widget(MDLabel(text="Sao lưu & Phục hồi", halign="center", font_style="H5"))
        
        # Backup buttons
        backup_card = MDCard(size_hint_y=None, height=dp(120), elevation=2, radius=[dp(15)])
        backup_layout = MDBoxLayout(orientation='vertical', padding=dp(15))
        MDRaisedButton(text="📤 Backup ZIP", size_hint_y=None, height=dp(50),
                      on_release=self.backup_data).add_to(backup_layout)
        MDFlatButton(text="📱 Share qua Telegram", size_hint_y=None, height=dp(40),
                    on_release=self.share_telegram).add_to(backup_layout)
        backup_card.add_widget(backup_layout)
        
        # Restore buttons
        restore_card = MDCard(size_hint_y=None, height=dp(100), elevation=2, radius=[dp(15)])
        restore_layout = MDBoxLayout(orientation='vertical', padding=dp(15))
        MDRaisedButton(text="📥 Chọn file ZIP để Restore", size_hint_y=None, height=dp(50),
                      on_release=self.restore_data).add_to(restore_layout)
        restore_card.add_widget(restore_layout)
        
        # Upload Google Drive (optional)
        if platform != 'android':
            drive_btn = MDRaisedButton(text="☁️ Upload Google Drive", size_hint_y=None, height=dp(50),
                                     on_release=self.upload_gdrive)
            layout.add_widget(drive_btn)
        
        layout.add_widget(backup_card)
        layout.add_widget(restore_card)
        
        self.add_widget(layout)
    
    def backup_data(self, instance):
        filename = f"saligrid_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.dm.export_all_data(filename)
        MDApp.get_running_app().show_snackbar(f"Backup: {os.path.basename(zip_path)}")
    
    def share_telegram(self, instance):
        filename = f"saligrid_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.dm.export_all_data(filename)
        
        if platform == 'android':
            from plyer import intent
            intent.share_file(zip_path, subject="SA LI GRID Backup", text="Dữ liệu xe tải")
        else:
            MDApp.get_running_app().show_snackbar("Share file: " + zip_path)
    
    def restore_data(self, instance):
        if platform == 'android':
            from plyer import filechooser
            filechooser.open_file(on_selection=self.on_file_select)
        else:
            MDApp.get_running_app().show_snackbar("Chọn file ZIP trên Android")
    
    def on_file_select(self, selection):
        if selection:
            zip_path = selection[0]
            if self.dm.import_data(zip_path):
                MDApp.get_running_app().show_snackbar("✅ Restore thành công!")
                self.manager.switch_to(self.manager.get_screen("main"))
            else:
                MDApp.get_running_app().show_snackbar("❌ Lỗi file backup!")
    
    def upload_gdrive(self, instance):
        # Simple HTTP upload (cần server riêng hoặc Google Drive API)
        MDApp.get_running_app().show_snackbar("Tính năng Google Drive đang phát triển")

# Cập nhật MainScreen để thêm Backup
class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self.menu_items = [
            {"text": "Bắt đầu chuyến"},
            {"text": "Kết thúc chuyến"},
            {"text": "Ghi chú chi phí"},
            {"text": "Sức khỏe xe"},
            {"text": "Cấu hình"},
            {"text": "💾 Backup & Restore"}  # Thêm mới
        ]
        self.build_ui()
    
    # Giữ nguyên các method khác, chỉ thêm case mới
    def on_menu_click(self, text):
        if "Bắt đầu" in text:
            self.manager.switch_to(self.manager.get_screen("trip"))
        elif "Kết thúc" in text:
            self.manager.switch_to(self.manager.get_screen("endtrip"))
        elif "Ghi chú" in text:
            self.manager.switch_to(self.manager.get_screen("note"))
        elif "Cấu hình" in text:
            self.manager.switch_to(self.manager.get_screen("config"))
        elif "Sức khỏe xe" in text:
            MDApp.get_running_app().show_health_report()
        elif "Backup" in text:
            self.manager.switch_to(self.manager.get_screen("backup"))

# Các screen khác (ConfigScreen, TripScreen, etc.) giữ nguyên như code trước

class VehicleApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dm = DataManager()
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_design = True
        
        sm = MDScreenManager()
        sm.add_widget(MainScreen())
        sm.add_widget(TripScreen())
        sm.add_widget(EndTripScreen())
        sm.add_widget(NoteScreen())
        sm.add_widget(ConfigScreen())
        sm.add_widget(BackupScreen())  # Thêm mới
        
        return sm
    
    def show_snackbar(self, text):
        from kivymd.uix.snackbar import Snackbar
        Snackbar(text=text).open()
    
    def show_health_report(self):
        # Giữ nguyên như trước
        pass

if __name__ == '__main__':
    VehicleApp().run()
