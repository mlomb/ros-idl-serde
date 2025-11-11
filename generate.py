import re
import subprocess
import os
import shutil

BASE_ROS_DIR = "/opt/ros/humble/share/"

# iterate recursive through the BASE_ROS_DIR looking for .idl files
idl_files = []

for root, dirs, files in os.walk(BASE_ROS_DIR):
    for idl_file in files:
        path = os.path.join(root, idl_file)
        if path.endswith(".idl"):
            idl_files.append(path)

# add '#pragma once' to each IDL file
# this prevents multiple definitions in some IDL files
# see https://github.com/eProsima/Fast-DDS-Gen/issues/52#issuecomment-1712020458
for idl_file in idl_files:
    with open(idl_file, "r") as f:
        content = f.read()
    with open(idl_file, "w") as f:
        f.write("#pragma once\n")
        f.write(content)

for i, idl_file in enumerate(idl_files):
    # std_msgs/msg/Header
    basename = idl_file.replace(BASE_ROS_DIR, "").replace(".idl", "")

    # Header
    name = os.path.basename(idl_file).replace(".idl", "")

    try:
        # /out/std_msgs/msg/Header
        dst_base = os.path.join("/out", basename)

        # make sure folder tree exists
        os.makedirs(os.path.dirname(dst_base + ".idl"), exist_ok=True)

        # copy IDL
        shutil.copy(idl_file, dst_base + ".idl")

        # copy MSG if it exists
        msg_file = idl_file.replace(".idl", ".msg")
        if os.path.exists(msg_file):
            shutil.copy(msg_file, dst_base + ".msg")

        subprocess.run(
            [
                "fastddsgen",
                "-I", BASE_ROS_DIR,
                "-replace",
                "-typeros2",
                "-cs",
                "-replace",
                "-d", "/tmp",
                idl_file
            ],
            cwd=BASE_ROS_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # copy generated files to /out/<basename>.<extension>
        extensions = ["h", "cxx"]
        for extension in extensions:
            src = os.path.join("/tmp", f"{name}.{extension}")
            dst = os.path.join("/out", f"{dst_base}.{extension}")
            shutil.copy(src, dst)
        
        visited = []

        def collect_includes(file_path):
            if file_path in visited:
                return
            visited.append(file_path)
            for m in re.finditer(r'#include\s+"([^"]+)"', open(file_path).read()):
                collect_includes(BASE_ROS_DIR + m.group(1))
        
        # recursively collect all included IDL files from this one
        collect_includes(idl_file)

        # build MCAP schema
        # see https://mcap.dev/spec/registry#ros2idl
        mcap_schema = ""
        for f in visited:
            content = open(f).read()
            incl_basename = f.replace(BASE_ROS_DIR, "").replace(".idl", "")
            content = content.replace("#pragma once", "")
            content = re.sub(r'^#include.*\n', '', content, flags=re.MULTILINE)
            mcap_schema += "=" * 80 + f"\nIDL: {incl_basename}\n" + content + "\n"

        # insert after the line "public:" in the .h file
        with open(dst_base + ".h", "r") as f:
            content = f.read()
        with open(dst_base + ".h", "w") as f:
            f.write(content.replace("public:", f"public:\nstatic constexpr std::string_view MCAP_SCHEMA = R\"({mcap_schema})\";"))

        print(f"[{i+1}/{len(idl_files)}] Generated {basename}")
    except Exception as e:
        print(f"[{i+1}/{len(idl_files)}] Error generating {basename}: {e}")

print("Done")
