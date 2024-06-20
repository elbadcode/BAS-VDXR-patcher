import os,json,sys,shutil,tkinter.messagebox as tk



def patch_config(read_only=None):
    user_prof = os.environ['USERPROFILE']
    os.chdir(user_prof)
    config_dir = os.path.join(user_prof, "AppData\\Roaming\\Virtual Desktop")
    config_path = os.path.join(config_dir, "GameSettings.json")
    os.chdir(config_dir)
    with open(config_path, "r+") as f:
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

def replace_dll(game_path):
    plugins = os.path.join(game_path, "BladeAndSorcery_Data\\Plugins\\x86_64")
    os.chdir(plugins)
    try:
        plugin_path = os.path.join(plugins, "OVRPlugin.dll")
        print(plugin_path)
        try:
            os.rename("OVRPlugin.dll", "OVRPlugin.bak")
        except FileExistsError:
            os.remove(plugin_path)
        except FileNotFoundError:
            pass
        shutil.copyfile(my_dll_path, plugin_path)
        if os.path.exists(plugin_path):
            print('success!')
            return True
    except Exception as e:
        os.chdir(os.path.dirname(my_dll_path))
        with open("ErrorLog.txt", "w") as f:
            print(e,file=f)
        return False

def get_game_path():
    try:
        if len(sys.argv) > 1:
            arg = str(sys.argv[1])
            try:
                if arg.endswith("BladeAndSorcery") and os.path.exists(arg):
                    os.chdir(arg)
                    replace_dll(arg)
                elif arg.endswith('.vdf'):
                    with open(arg, "r") as f:
                        f = str(f.readlines()[1:])
                        library_data = json.loads(f)
                        for i in range(len(library_data)):
                            if "629730" in library_data[i][apps]:
                                game_path = os.path.join(library_data[i][path], "steamapps\\common\\Blade & Sorcery")
                                try:
                                    os.chdir(game_path)
                                    return replace_dll(game_path)
                                except Exception as e:
                                    print(e)
                                    tk.showwarning("Something went wrong try running from game directory")
                                    return False
            except Exception as e:
                print(e)
                tkinter.showwarning("Something went wrong try running from game directory")
                return False
        elif "BladeAndSorcery" in str(os.getcwd()):
            try_path = str(os.getcwd())
            if try_path.endswith("BladeAndSorcery"):
                return replace_dll(try_path)
            while not try_path.endswith("BladeAndSorcery"):
                try_path = os.path.abspath(os.path.join(try_path, '..'))
            if try_path.endswith("BladeAndSorcery"):
                return replace_dll(try_path)
        else:
            game_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blade & Sorcery"
            if os.path.exists(game_path):
                return replace_dll(game_path)
    except IndexError:
        pass

global my_dll_path
my_dll_path = os.path.join(os.getcwd(), "OVRPlugin.dll")
print(my_dll_path)
patch_config()
if get_game_path():
    tk.showinfo("Success", "Everything should be patched just make sure to run as oculus mode and set VDXR in VD")
else:
    tk.showwarning("Error", "Something went wrong, try again with both files in the game directory or install the dll manually")
    