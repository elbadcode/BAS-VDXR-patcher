import os,json,sys,shutil,tkinter.messagebox as tk, pefile

def patch_config(read_only=None):
    user_prof = os.environ['USERPROFILE']
    os.chdir(user_prof)
    config_dir = os.path.join(user_prof, "AppData\\Roaming\\Virtual Desktop")
    config_path = os.path.join(config_dir, "GameSettings.json")
    os.chdir(config_dir)
    with open(config_path, "r+") as f:
        try:
            config_data = json.load(f)
            game_list = config_data["SteamProductInfos"]
            bas_settings = game_list["629730"]
            if not read_only:
                print("Previous values: ")
                print(bas_settings)
                tk.showinfo("Previous values", bas_settings)
            else:
                print("Patched values: ")
                print(bas_settings)
                tk.showinfo("Patched values", bas_settings)
            bas_settings = {
                    "OpenXRSupport": True,
                    "Executable": "BladeAndSorcery.exe",
                    "Arguments": "-vrmode oculus"
            }
            game_list["629730"] = bas_settings
            config_data["SteamProductInfos"] = game_list
            f.seek(0)
            if not read_only:
                json.dump(config_data, f, indent=2)
                patch_config(read_only=True)
        except Exception as e:
            os.chdir(base_dir)
            with open("ErrorLog.txt", "w") as f:
                print(e,file=f)


def replace_dll(game_path):
    plugins = os.path.join(game_path, "BladeAndSorcery_Data\\Plugins\\x86_64")
    os.chdir(plugins)
    try:
        plugin_path = os.path.join(plugins, "OVRPlugin.dll")
        if not os.path.exists(plugin_path):
            estr = f"Didn't find the original DLL at {plugin_path}. Are you sure your game is installed here?"
            tk.showwarning("Error", estr)
            return False
        print(plugin_path)
        try:
            #this is honestly pointless and you should always just verify files but just in case some user cries about deleting their files...
            os.rename("OVRPlugin.dll", "OVRPlugin.bak")
        #on subsequent runs this will always occur
        except FileExistsError:
            backup = os.path.join(plugins,"OVRPlugin.bak")
            #remove any nonsense backups of the modded plugin and remove if the current plugin is newer than backup
            if os.path.getsize(backup) == os.path.getsize(my_dll_path) or os.path.getmtime(plugin_path) >= os.path.getmtime(backup):
                print(os.path.getsize(backup))
                print(os.path.getsize(my_dll_path))
                os.remove(backup)
                os.rename("OVRPlugin.dll", "OVRPlugin.bak")
            else:
                os.remove(plugin_path)
        #this shouldn't ever happen since we checked for it...
        except FileNotFoundError:
            print('filenotfound')
            return False
        except PermissionError:
            tk.showwarning('file is in use. make sure to close the game')
        shutil.copyfile(my_dll_path, plugin_path)
        if os.path.exists(plugin_path):
            try:
                ppe = pefile.PE(plugin_path)
                ppeDT = ppe.FILE_HEADER.TimeDateStamp
                print(ppeDT)
                if ppeDT == myPEdt and os.path.getsize(plugin_path) == 9701432:
                    tk.showinfo('Success','Successfully replaced DLL!')
                    return True
                else:
                    tk.showinfo('Info', 'Plugin info does not match replacement, check error log for info')
                    size = os.path.getsize(plugin_path)
                    time = ppeDT
                    os.chdir(base_dir)
                    with open("ErrorLog.txt", "w") as f:
                        print(f"plugin size: {size}\n timestamp: {time}", file=f)
                    return False
            except Exception as e:
                print(e)
    except Exception as e:
        os.chdir(base_dir)
        with open("ErrorLog.txt", "w") as f:
            print(e,file=f)
        return False

def get_game_path():
    try:
        if len(sys.argv) > 1:
            arg = str(sys.argv[1])
            try:
                #startup arg pathfinding
                if arg.endswith("Blade & Sorcery") and os.path.exists(arg):
                    os.chdir(arg)
                    replace_dll(arg)
            except Exception as e:
                print(e)
                tk.showwarning("Something went wrong try running from game directory")
                return False
        elif "Blade & Sorcery" in str(os.getcwd()):
            try_path = str(os.getcwd())
            if try_path.endswith("Blade & Sorcery"):
                return replace_dll(try_path)
            # go up a folder until we reach the base folder
            while not try_path.endswith("Blade & Sorcery"):
                try_path = os.path.abspath(os.path.join(try_path, '..'))
            return replace_dll(try_path)
        else:
            game_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blade & Sorcery"
            if os.path.exists(game_path):
                return replace_dll(game_path)
    except IndexError:
        #not a real error, python always assigns the script startup dir as the first startup arg but asking if we have any additional args and then acting on those args after confirming they exist always throws an index error.
        # its baffling but anyway users dont need to know since we move to default behavior
        pass

global my_dll_path
my_dll_path = os.path.join(os.getcwd(), "OVRPlugin.dll")
global myPE
myPE = pefile.PE(my_dll_path)
global myPEdt
myPEdt = myPE.FILE_HEADER.TimeDateStamp
global base_dir
base_dir = os.path.dirname(my_dll_path)
print(my_dll_path)
patch_config()
if get_game_path():
    tk.showinfo("Success", "Everything should be patched just make sure to run as oculus mode and set VDXR in VD")
    exit()
else:
    tk.showwarning("Error", "Something went wrong, try again with both files in the game directory or install the dll manually")
    exit()
    
