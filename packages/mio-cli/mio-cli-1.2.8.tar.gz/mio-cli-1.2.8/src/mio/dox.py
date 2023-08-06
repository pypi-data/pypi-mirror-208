# Copyright 2021-2023 Datum Technology Corporation
# SPDX-License-Identifier: GPL-3.0
########################################################################################################################

from mio import common
from mio import cache
from mio import cfg
from mio import eal
import os

import subprocess


def gen_doxygen(ip_str, inc_deps=True, inc_tags=True):
    vendor, name = common.parse_dep(ip_str)
    if vendor == "":
        ip = cache.get_anon_ip(name, True)
    else:
        ip = cache.get_ip(vendor, name, True)
    ip_name = f"{ip.vendor}/{ip.name}"
    common.dbg(f"Running doxygen on '{ip_name}'")
    ip_src_path      = ip.path + "/" + ip.src_path
    ip_bin_path      = ip.path + "/" + ip.scripts_path
    ip_docs_path     = ip.path + "/" + ip.docs_path
    ip_examples_path = ip.path + "/" + ip.examples_path
    
    dep_example_paths = ""
    dep_src_paths     = ""
    dep_docs_paths    = ""
    
    common.create_dir(f"{ip_docs_path}")
    common.create_dir(f"{ip_docs_path}/dox_out")
    common.create_dir(f"{ip_docs_path}/dox_out/html")
    
    if inc_deps:
        # Local code
        if ip.has_dut:
            if ip.dut != None:
                dut_ip = ip.dut.target_ip_model
                if (not dut_ip.from_ip_server) and (not dut_ip.is_encrypted):
                    dep_example_paths += f"{dut_ip.path}/{dut_ip.examples_path} "
                    dep_src_paths     += f"{dut_ip.path}/{dut_ip.src_path} "
                    dep_docs_paths    += f"{dut_ip.path}/{dut_ip.docs_path} "
        deps = ip.get_ordered_deps()
        for dep in deps:
            if (not dep.from_ip_server) and (not dep.is_encrypted):
                dep_example_paths += f"{dep.path}/{dep.examples_path} "
                dep_src_paths     += f"{dep.path}/{dep.src_path} "
                dep_docs_paths    += f"{dep.path}/{dep.docs_path} "
    
    args  = " PROJECT_NAME='"  + ip.full_name + "'"
    args += " PROJECT_BRIEF='" + ip.full_name + "'"
    args += " IP_NAME='" + ip.name + "'"
    args += " PROJECT_NUMBER='" + ip.name + "'"
    args += " EXAMPLE_PATH=" + os.path.relpath(ip_examples_path, ip.path)
    args += " OUTPUT_PATH="  + os.path.relpath(ip_docs_path, ip.path) + "/dox_out"
    args += " SRC_PATH='" + os.path.relpath(ip_src_path, ip.path) + f" {dep_src_paths}'"
    args += " MIO_HOME=" + cfg.mio_data_src_dir + " IP_NAME=" + ip_name
    args += " DOCS_PATH+=" + os.path.relpath(ip_docs_path, ip.path)
    
    ip_docs_path = os.path.relpath(ip_docs_path, ip.path)
    args += f" GENERATE_TAGFILE='{ip_docs_path}/dox_out/{ip.vendor}__{ip.name}.tag'"
    if inc_tags:
        tag_files = ""
        if ip.has_dut:
            dut_ip = ip.dut.target_ip_model
            if dut_ip.from_ip_server:
                tag_files += f"{dut_ip.path}/{dut_ip.docs_path}/dox_out/{dut_ip.vendor}__{dut_ip.name}.tag={dut_ip.path}/{dut_ip.docs_path}/dox_out/html "
        deps = ip.get_ordered_deps()
        for dep in deps:
            if dep.from_ip_server and (dep.name != "uvml_mio_lic"):
                tag_files += f"{dep.path}/{dep.docs_path}/dox_out/{dep.vendor}__{dep.name}.tag={dep.path}/{dep.docs_path}/dox_out/html "
        if tag_files != "":
            args += f" TAGFILES='{tag_files}'"
    
    #args += " IMAGE_PATH=" + ip_path + "/" + ip_metadata['structure']['docs-path']
    #args += " INPUT+="     + ip_path + "/" + ip_metadata['structure']['docs-path']
    #for input_dir in ip_metadata['hdl-src']['directories']:
    #    if input_dir != "." and input_dir != "":
    #        args += " INPUT+=" + ip_src_path + "/" + input_dir
    #    else:
    #        args += " INPUT+=" + ip_src_path
    common.banner(f"Invoking Doxygen on IP '{ip_name}' ({ip_src_path})")
    eal.launch_eda_bin(args + " doxygen", [cfg.mio_data_src_dir + "/doxygen.private.cfg"], wd=ip.path, output=cfg.dbg)
    common.info("Done.  To view documentation: `firefox " + ip.path + "/" + ip.docs_path + "/dox_out/html/index.html &`")
