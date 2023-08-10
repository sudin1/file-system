import os
import platform
import ctypes
from ctypes import wintypes

class FileSystem:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.is_windows = platform.system() == 'Windows'

    def create_file(self, filename, permissions=None):
        filepath = os.path.join(self.current_directory, filename)
        if os.path.exists(filepath):
            print(f"Error: File '{filename}' already exists.")
            return

        with open(filepath, 'w') as file:
            print(f"File '{filename}' created successfully.")

        if permissions is not None:
            self.set_permissions(filename, permissions)

    def delete_file(self, filename):
        filepath = os.path.join(self.current_directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File '{filename}' deleted successfully.")
        else:
            print(f"Error: File '{filename}' does not exist.")

    def read_file(self, filename):
        filepath = os.path.join(self.current_directory, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                content = file.read()
                print(f"--- Content of '{filename}' ---")
                print(content)
        else:
            print(f"Error: File '{filename}' does not exist.")

    def write_file(self, filename):
        filepath = os.path.join(self.current_directory, filename)
        if os.path.exists(filepath):
            print(f"--- Writing content to '{filename}' ---")
            content = input("Enter the content:\n")
            with open(filepath, 'w') as file:
                file.write(content)
                print(f"Content written successfully to '{filename}'.")
        else:
            print(f"Error: File '{filename}' does not exist.")

    def set_permissions(self, filename, permissions):
        filepath = os.path.join(self.current_directory, filename)
        if os.path.exists(filepath):
            if self.is_windows:
                try:
                    security_attributes = ctypes.c_void_p()
                    security_descriptor = ctypes.c_void_p()
                    if ctypes.windll.advapi32.GetFileSecurityW(
                        filepath,
                        ctypes.DACL_SECURITY_INFORMATION | ctypes.OWNER_SECURITY_INFORMATION,
                        ctypes.byref(security_descriptor),
                        0,
                    ):
                        owner_sid = wintypes.PSID()
                        owner_defaulted = wintypes.BOOL()
                        if ctypes.windll.advapi32.GetSecurityDescriptorOwner(
                            security_descriptor,
                            ctypes.byref(owner_sid),
                            ctypes.byref(owner_defaulted),
                        ):
                            name = ctypes.create_unicode_buffer(256)
                            domain = ctypes.create_unicode_buffer(256)
                            name_size = wintypes.DWORD(len(name))
                            domain_size = wintypes.DWORD(len(domain))
                            sid_name_use = wintypes.DWORD()
                            if ctypes.windll.advapi32.LookupAccountSidW(
                                None,
                                owner_sid,
                                name,
                                ctypes.byref(name_size),
                                domain,
                                ctypes.byref(domain_size),
                                ctypes.byref(sid_name_use),
                            ):
                                owner = f"{domain.value}\\{name.value}"
                                print(f"Owner: {owner}")
                except OSError:
                    print(f"Failed to get owner information for '{filename}'.")
            else:
                try:
                    os.chmod(filepath, permissions)
                    print(f"Permissions set successfully for '{filename}'.")
                except OSError:
                    print(f"Failed to set permissions for '{filename}'.")
        else:
            print(f"Error: File '{filename}' does not exist.")

    def change_directory(self, new_directory):
        new_path = os.path.join(self.current_directory, new_directory)
        if os.path.isdir(new_path):
            self.current_directory = new_path
            print(f"Current directory changed to '{self.current_directory}'.")
        else:
            print(f"Error: Directory '{new_directory}' does not exist.")

    def list_directory(self):
        contents = os.listdir(self.current_directory)
        print(f"--- Contents of '{self.current_directory}' ---")
        for item in contents:
            item_path = os.path.join(self.current_directory, item)
            if os.path.isdir(item_path):
                item = item + "/"
            owner = self.get_file_owner(item_path)
            print(f"{item}\tOwner: {owner}")

    def get_file_owner(self, filepath):
        if self.is_windows:
            try:
                security_attributes = ctypes.c_void_p()
                security_descriptor = ctypes.c_void_p()
                if ctypes.windll.advapi32.GetFileSecurityW(
                    filepath,
                    ctypes.DACL_SECURITY_INFORMATION | ctypes.OWNER_SECURITY_INFORMATION,
                    ctypes.byref(security_descriptor),
                    0,
                ):
                    owner_sid = wintypes.PSID()
                    owner_defaulted = wintypes.BOOL()
                    if ctypes.windll.advapi32.GetSecurityDescriptorOwner(
                        security_descriptor,
                        ctypes.byref(owner_sid),
                        ctypes.byref(owner_defaulted),
                    ):
                        name = ctypes.create_unicode_buffer(256)
                        domain = ctypes.create_unicode_buffer(256)
                        name_size = wintypes.DWORD(len(name))
                        domain_size = wintypes.DWORD(len(domain))
                        sid_name_use = wintypes.DWORD()
                        if ctypes.windll.advapi32.LookupAccountSidW(
                            None,
                            owner_sid,
                            name,
                            ctypes.byref(name_size),
                            domain,
                            ctypes.byref(domain_size),
                            ctypes.byref(sid_name_use),
                        ):
                            return f"{domain.value}\\{name.value}"
            except OSError:
                pass
        else:
            try:
                return os.stat(filepath).st_uid
            except OSError:
                pass
        return "Unknown"

    def run(self):
        while True:
            print("\n--- File System Menu ---")
            print("1. Create File")
            print("2. Delete File")
            print("3. Read File")
            print("4. Write File")
            print("5. Set Permissions")
            print("6. Change Directory")
            print("7. List Directory")
            print("8. Exit")

            choice = input("Enter your choice (1-8): ")
            if choice == '1':
                filename = input("Enter the filename: ")
                permissions = None
                if self.is_windows:
                    permissions = int(input("Enter the permissions (in octal format, e.g., 644): "), 8)
                self.create_file(filename, permissions)
            elif choice == '2':
                filename = input("Enter the filename: ")
                self.delete_file(filename)
            elif choice == '3':
                filename = input("Enter the filename: ")
                self.read_file(filename)
            elif choice == '4':
                filename = input("Enter the filename: ")
                self.write_file(filename)
            elif choice == '5':
                filename = input("Enter the filename: ")
                permissions = int(input("Enter the permissions (in octal format, e.g., 644): "), 8)
                self.set_permissions(filename, permissions)
            elif choice == '6':
                new_directory = input("Enter the new directory: ")
                self.change_directory(new_directory)
            elif choice == '7':
                self.list_directory()
            elif choice == '8':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    file_system = FileSystem()
    file_system.run()