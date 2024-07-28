import os
import zipfile
from pyjd import Decompiler

def decompile_class_file(jar_file, class_file):
    decompiler = Decompiler()
    with zipfile.ZipFile(jar_file, 'r') as jar:
        with jar.open(class_file) as class_data:
            class_bytes = class_data.read()
            return decompiler.decompile(class_bytes)

def check_mod_side(mod_jar_path):
    client_only_indicators = [
        "net.minecraft.client.Minecraft",
        "net.minecraft.client.gui",
        "net.minecraft.client.renderer",
        "net.minecraft.client.audio",
        "@SideOnly(Side.CLIENT)",
        "cpw.mods.fml.relauncher.Side.CLIENT"
    ]
    
    with zipfile.ZipFile(mod_jar_path, 'r') as mod_jar:
        for file in mod_jar.namelist():
            if file.endswith(".class"):
                try:
                    source_code = decompile_class_file(mod_jar_path, file)
                    if any(indicator in source_code for indicator in client_only_indicators):
                        return "Client-Side"
                except Exception as e:
                    print(f"Error decompiling {file}: {e}")
    return "Server-Side or Both"

def check_all_mods(directory_path):
    results = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".jar"):
            mod_path = os.path.join(directory_path, filename)
            side = check_mod_side(mod_path)
            results[filename] = side
    return results

# Example usage
directory_path = "/home/flashgnash/test-mods/"
mod_results = check_all_mods(directory_path)

for mod, side in mod_results.items():
    print(f"The mod {mod} is likely: {side}")
