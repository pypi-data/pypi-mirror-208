# Copyright 2021-2023 Datum Technology Corporation
# SPDX-License-Identifier: GPL-3.0
########################################################################################################################




from mio import cfg
from mio import clean
from mio import cov
from mio import dox
from mio import results
from mio import cache
from mio import common
from mio import eal
from mio import install
from mio import doctor
from tqdm import tqdm
from tqdm import trange
from threading import Thread
from multiprocessing.pool import ThreadPool
from threading import BoundedSemaphore
import threading
import time
import os
from datetime import datetime
import yaml
from yaml.loader import SafeLoader
import math
import re
import atexit
import tarfile




bwrap_ignore_list = [
    "xsim.dir", ".str", ".Xil", ".jou", ".log", ".wdb", ".vcd", ".log", ".sdb", ".rlx", ".pb", ".o", ".png", ".jpg",
    ".svg", ".vsdx", ".docx", ".xlsx", ".pptx", ".md", "sync", "workspace"
]

bwrap_ignore_dirs = [ ".git", ".svn" ]

regex_define_pattern  = "\+define\+((?:\w|_|\d)+)(?:\=((?:\w|_|\d)+))?"
regex_plusarg_pattern = "\+((?:\w|_|\d)+)(?:\=((?:\w|_|\d)+))?"
seconds_waited = 0
num_deps_to_compile = 0
sem = BoundedSemaphore(1)
pbar = None
est_time = 0
overtime = True


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()




class SimulationJob:
    """Simulation Job model"""
    
    def __init__(self, ip_str):
        self.id              = 0
        self.vendor, self.ip = common.parse_dep(ip_str)
        self.simulator       = ""
        self.fsoc            = False
        self.compile         = False
        self.elaborate       = False
        self.simulate        = False
        self.test            = ""
        self.seed            = 0
        self.max_errors      = 0
        self.gui             = False
        self.verbosity       = ""
        self.waves           = False
        self.cov             = False
        self.dry_run         = False
        self.raw_args        = []
        self.target_name     = "default"
        self.cmp_args        = {}
        self.elab_args       = {}
        self.sim_args        = {}
        
        self.bwrap           = False
        self.bwrap_commands  = []
        self.bwrap_flists    = {}
        
        self.is_regression        = False
        self.regression_name      = ""
        self.regression_timestamp = ""
        
        self.timestamp_start    = ""
        self.timestamp_end      = ""
        self.filelist_path      = ""
        self.results_path       = ""
        self.results_dir_name   = ""
        self.cmp_log_file_path  = ""
        self.elab_log_file_path = ""
        self.sim_log_file_path  = ""
        




def main(sim_job):
    global est_time
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    common.dbg(f"Starting simulation job: '{sim_job.vendor}/{sim_job.ip}'")
    if sim_job.vendor == "":
        ip = cache.get_anon_ip(sim_job.ip, True)
    else:
        ip = cache.get_ip(sim_job.vendor, sim_job.ip, True)
    if ip == None:
        common.fatal(f"Cannot find IP '{sim_job.vendor}/{sim_job.ip}'")
    ip_str = f"{ip.vendor}/{ip.name}"
    if sim_job.target_name == "default":
        ip_target_str = f"{ip.vendor}/{ip.name}"
    else:
        ip_target_str = f"{ip.vendor}/{ip.name}#{sim_job.target_name}"
    
    if sim_job.compile:
        if not ip.are_deps_installed():
            deps_to_install = ip.get_deps_to_install()
            if len(deps_to_install) > 0:
                install_deps_str = ""
                while (install_deps_str != "y") and (install_deps_str != "n"):
                    install_deps_str = common.prompt(f"{len(deps_to_install)} dependencies must first be installed.  Would you like to do so now? [y/n]").strip().lower()
                if install_deps_str == "y":
                    local_str = ""
                    while (local_str != "y") and (local_str != "n"):
                        local_str = common.prompt("Local install (vs. global)? [y/n]").strip().lower()
                    if local_str == "y":
                        global_install = False
                    else:
                        global_install = True
                    install.install_ip_and_deps(ip.vendor, ip.name, global_install)
                else:
                    common.fatal("Cannot continue without first installing '" + ip_str + "' IP dependencies.")
    
    if not doctor.check_simulator_executables(sim_job.simulator):
        common.fatal("Simulator '" + sim_job.simulator + "' not installed properly or environment variable missing")
    
    convert_cli_args_to_defines (sim_job)
    convert_cli_args_to_plusargs(sim_job)
    create_sim_directories      (sim_job)
    check_dependencies(ip)
    check_dut         (ip)
    
    eal.init_workspace(sim_job)
    
    fsoc_core_name = ""
    fsoc_core_flist_path = ""
    if ip.dut_ip_type == "fsoc":
        if sim_job.fsoc:
            common.info(f"Processing FuseSoC Core '{ip.dut_core.name}' ...")
            fsoc_core_flist_path = eal.invoke_fsoc(ip, ip.dut_core, sim_job)
            if not sim_job.compile and not sim_job.elaborate and not sim_job.simulate:
                common.info(f"Done.")
        fsoc_core_name = ip.dut_core
    elif ip.dut_ip_type == "vivado":
        dut_ip_str = f"{ip.dut.vendor}/{ip.dut.target_ip}"
        common.info(f"Compiling Vivado Project DUT IP '{dut_ip_str}' ...")
        est_time = get_ip_cmp_est(ip.dut.target_ip_model, sim_job)
        if est_time > 0:
            pool = ThreadPool(processes=1)
            pool.apply_async(progress_bar)
            eal.cmp_vivado_project(ip.dut.target_ip_model, sim_job, True, ip)
            fill_progress_bar()
            pool.terminate()
            pool.join()
        else:
            eal.cmp_vivado_project(ip.dut.target_ip_model, sim_job)
    
    if sim_job.compile and sim_job.elaborate:
        if sim_job.simulator == common.simulators_enum.VIVADO:
            common.info(f"Compiling {ip_target_str} ...")
            est_time = get_ip_cmp_est(ip, sim_job)
            if est_time > 0:
                pool = ThreadPool(processes=1)
                pool.apply_async(progress_bar)
                eal.cmp_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
                fill_progress_bar()
                pool.terminate()
                pool.join()
            else:
                eal.cmp_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
            common.info(f"Elaborating {ip_target_str} ...")
            est_time = get_ip_elab_est(ip, sim_job)
            if est_time > 0:
                pool = ThreadPool(processes=1)
                pool.apply_async(progress_bar)
                eal.elab_ip(ip, sim_job)
                fill_progress_bar()
                pool.terminate()
                pool.join()
            else:
                eal.elab_ip(ip, sim_job)
        else:
            common.info(f"Compiling+Elaborating {ip_target_str} ...")
            est_time = get_ip_gen_image_est(ip, sim_job)
            if est_time > 0:
                pool = ThreadPool(processes=1)
                pool.apply_async(progress_bar)
                eal.gen_image_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
                fill_progress_bar()
                pool.terminate()
                pool.join()
            else:
                eal.gen_image_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
    elif sim_job.compile:
        common.info(f"Compiling {ip_target_str} ...")
        est_time = get_ip_cmp_est(ip, sim_job)
        if est_time > 0:
            pool = ThreadPool(processes=1)
            pool.apply_async(progress_bar)
            if ip.vproj_name == "":
                eal.cmp_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
            else:
                eal.cmp_vivado_project(ip, sim_job)
            fill_progress_bar()
            pool.terminate()
            pool.join()
        else:
            eal.cmp_ip(ip, sim_job, fsoc_core_name, fsoc_core_flist_path)
    elif sim_job.elaborate:
        common.info(f"Elaborating {ip_target_str} ...")
        est_time = get_ip_elab_est(ip, sim_job)
        if est_time > 0:
            pool = ThreadPool(processes=1)
            pool.apply_async(progress_bar)
            eal.elab_ip(ip, sim_job)
            fill_progress_bar()
            pool.terminate()
            pool.join()
        else:
            eal.elab_ip(ip, sim_job)
    
    if not sim_job.is_regression:
        if sim_job.simulate:
            common.banner(f"Simulating {ip_target_str} ...")
            if sim_job.gui and sim_job.simulator == common.simulators_enum.METRICS:
                common.warning("The Metrics Cloud Simulator does not support GUI mode")
            eal.simulate(ip, sim_job)
    
    if not sim_job.is_regression:
        if sim_job.compile and sim_job.elaborate:
            if sim_job.simulator == common.simulators_enum.VIVADO:
                print_end_of_compilation_message(ip, sim_job)
                print_end_of_elaboration_message(ip, sim_job)
            else:
                print_end_of_gen_image_message(ip, sim_job)
        elif sim_job.compile:
            print_end_of_compilation_message(ip, sim_job)
        elif sim_job.elaborate:
            print_end_of_elaboration_message(ip, sim_job)
        if sim_job.simulate:
            print_end_of_simulation_message(ip, sim_job)
    
    if sim_job.bwrap:
        bubble_wrap(sim_job)



def convert_cli_args_to_defines(sim_job):
    defines = {}
    args = sim_job.raw_args
    if args != None:
        if type(args) is list:
            for item in args:
                regex = "\+define\+(\w+)(?:\=(\w+))?"
                result = re.match(regex, item)
                if result:
                    if len(result.groups()) > 1:
                        arg_name  = result.group(1)
                        arg_value = result.group(2)
                        if arg_value == None:
                            arg_value = ""
                    elif len(result.groups()) == 1:
                        arg_name  = result.group(1)
                        arg_value = ""
                    else:
                        continue
                else:
                    continue
                defines[arg_name] = arg_value
                common.dbg("Added define '" + arg_name + "' with value '" + arg_value + "' to list")
        else:
            all_args = re.sub("\"", "", args)
            for arg in all_args:
                result = re.match(regex_define_pattern, arg)
                if result:
                    define_name = result.group(1)
                    if len(result.groups()) > 1:
                        define_value = result.group(2)
                        if define_value == None:
                            arg_value = ""
                    else:
                        define_value = ""
                    defines[define_name] = define_value
                    common.dbg("Added define '" + define_name + "' with value '" + define_value + "' to list")
    sim_job.cmp_args = defines


def convert_cli_args_to_plusargs(sim_job):
    define_regex = "\+define\+(\w+)(?:\=(\w+))?"
    plus_args = {}
    args = sim_job.raw_args
    if args != None:
        if type(args) is list:
            for item in args:
                result = re.match(define_regex, item)
                if result:
                    continue
                regex = "\+(\w+)(?:\=(\w+))?"
                result = re.match(regex, item)
                if result:
                    if len(result.groups()) > 1:
                        arg_name  = result.group(1)
                        arg_value = result.group(2)
                        if arg_value == None:
                            arg_value = ""
                    elif len(result.groups()) == 1:
                        arg_name  = result.group(1)
                        arg_value = ""
                    else:
                        continue
                else:
                    continue
                plus_args[arg_name] = arg_value
                common.dbg("Added plus arg '" + arg_name + "' with value '" + arg_value + "' to list")
        else:
            all_args = re.sub("\"", "", args)
            for arg in all_args:
                result = re.match(regex_define_pattern, arg)
                if not result:
                    result = re.match(regex_plusarg_pattern, arg)
                    if result:
                        arg_name = result.group(1)
                        if len(result.groups()) > 1:
                            arg_value = result.group(2)
                            if arg_value == None:
                                arg_value = ""
                        else:
                            arg_value = ""
                        plus_args[arg_name] = arg_value
                        common.dbg("Added plus arg '" + arg_name + "' with value '" + arg_value + "' to list")
    sim_job.sim_args = plus_args


def create_sim_directories(sim_job):
    common.dbg("Creating sim directories")
    common.create_dir(cfg.sim_dir)
    common.create_dir(cfg.sim_output_dir)
    common.create_dir(cfg.regr_results_dir)
    common.create_dir(cfg.sim_output_dir + "/viv"                     )
    common.create_dir(cfg.sim_output_dir + "/viv/cov_wd"              )
    common.create_dir(cfg.sim_output_dir + "/viv/cmp_out"             )
    common.create_dir(cfg.sim_output_dir + "/viv/sim_wd"              )
    common.create_dir(cfg.sim_output_dir + "/viv/regr_wd"             )
    common.create_dir(cfg.sim_output_dir + "/viv/so_libs"             )
    common.create_dir(cfg.sim_output_dir + "/vcs"                     )
    common.create_dir(cfg.sim_output_dir + "/vcs/cov_wd"              )
    common.create_dir(cfg.sim_output_dir + "/vcs/cmp_out"             )
    common.create_dir(cfg.sim_output_dir + "/vcs/sim_wd"              )
    common.create_dir(cfg.sim_output_dir + "/vcs/regr_wd"             )
    common.create_dir(cfg.sim_output_dir + "/vcs/so_libs"             )
    common.create_dir(cfg.sim_output_dir + "/xcl"                     )
    common.create_dir(cfg.sim_output_dir + "/xcl/cov_wd"              )
    common.create_dir(cfg.sim_output_dir + "/xcl/cmp_out"             )
    common.create_dir(cfg.sim_output_dir + "/xcl/sim_wd"              )
    common.create_dir(cfg.sim_output_dir + "/xcl/regr_wd"             )
    common.create_dir(cfg.sim_output_dir + "/xcl/so_libs"             )
    common.create_dir(cfg.sim_output_dir + "/qst"                     )
    common.create_dir(cfg.sim_output_dir + "/qst/cov_wd"              )
    common.create_dir(cfg.sim_output_dir + "/qst/cmp_out"             )
    common.create_dir(cfg.sim_output_dir + "/qst/sim_wd"              )
    common.create_dir(cfg.sim_output_dir + "/qst/regr_wd"             )
    common.create_dir(cfg.sim_output_dir + "/qst/so_libs"             )
    common.create_dir(cfg.sim_output_dir + "/riv"                     )
    common.create_dir(cfg.sim_output_dir + "/riv/cov_wd"              )
    common.create_dir(cfg.sim_output_dir + "/riv/cmp_out"             )
    common.create_dir(cfg.sim_output_dir + "/riv/sim_wd"              )
    common.create_dir(cfg.sim_output_dir + "/riv/regr_wd"             )
    common.create_dir(cfg.sim_output_dir + "/riv/so_libs"             )
    common.create_dir(cfg.sim_dir + "/cmp")
    common.create_dir(cfg.regr_results_dir)
    common.create_dir(cfg.sim_results_dir)


def check_dependencies(ip):
    for dep in ip.dependencies:
        #common.dbg(f"Checking dependency '{dep.vendor}/{dep.target_ip}'")
        found_ip = cache.get_ip(dep.vendor, dep.target_ip)
        if found_ip == None:
            common.fatal(f"Could not find IP dependency '{dep.vendor}/{dep.target_ip}'")
        else:
            check_dependencies(found_ip)


def check_dut(ip):
    if ip.dut_ip_type == "fsoc":
        pass
    else:
        if ip.dut != None:
            if ip.dut.target_ip_model == None:
                common.fatal(f"Did not resolve DUT dependency ('{ip.dut.vendor}/{ip.dut.target_ip}')!")




def bubble_wrap(sim_job):
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    run_script_path = f"{cfg.sim_dir}/run.sh"
    readme_path = f"{cfg.sim_dir}/README.txt"
    
    if sim_job.simulator == common.simulators_enum.VIVADO:
        bin_text = "MIO_VIVADO_HOME"
        bin_string = "/tools/vivado/bin"
    if sim_job.simulator == common.simulators_enum.METRICS:
        bin_text = "MIO_METRICS_HOME"
        bin_string = "/usr/local/bin"
    if sim_job.simulator == common.simulators_enum.VCS:
        bin_text = "MIO_VCS_HOME"
        bin_string = "/tools/vcs/bin"
    if sim_job.simulator == common.simulators_enum.QUESTA:
        bin_text = "MIO_QUESTA_HOME"
        bin_string = "/tools/questa/bin"
    if sim_job.simulator == common.simulators_enum.XCELIUM:
        bin_text = "MIO_XCELIUM_HOME"
        bin_string = "/tools/xcelium/bin"
    if sim_job.simulator == common.simulators_enum.RIVIERA:
        bin_text = "MIO_RIVIERA_HOME"
        bin_string = "/tools/riviera/bin"
    
    try:
        with open(run_script_path, 'w') as run_script_file:
            run_script_file.write(f"export PROJECT_ROOT_DIR=$(pwd)/..\n\n")
            for flist in sim_job.bwrap_flists:
                run_script_file.write(f"export {flist}={sim_job.bwrap_flists[flist]}\n")
            run_script_file.write("\n\n\n\n")
            for cmd in sim_job.bwrap_commands:
                cmd = cmd.replace(cfg.project_dir , "${PROJECT_ROOT_DIR}")
                cmd = cmd.replace("-f .mio/"      , "-f ${PROJECT_ROOT_DIR}/.mio/")
                cmd = cmd.replace(cfg.vivado_home , "${MIO_VIVADO_HOME}" )
                cmd = cmd.replace(cfg.metrics_home, "${MIO_METRICS_HOME}")
                cmd = cmd.replace(cfg.vcs_home    , "${MIO_VCS_HOME}"    )
                cmd = cmd.replace(cfg.xcelium_home, "${MIO_XCELIUM_HOME}")
                cmd = cmd.replace(cfg.questa_home , "${MIO_QUESTA_HOME}" )
                cmd = cmd.replace(cfg.riviera_home, "${MIO_RIVIERA_HOME}")
                run_script_file.write(f"{cmd}\n\n")
        common.info(f"Wrote {run_script_path}")
        with open(readme_path, 'w') as readme_file:
            readme_file.write(f"1. Set ${bin_text}.  Ex: export {bin_text}={bin_string}\n")
            readme_file.write(f"2. Run: bash ./run.sh\n")
        common.info(f"Wrote {readme_path}")
        
        tarball_filename = f"{sim_job.ip}.{sim_job.test}.{sim_job.seed}.{sim_str}.tgz"
        tarball_path = f"{cfg.project_dir}/../{tarball_filename}"
        common.info(f"Writing {tarball_path} ...")
        with tarfile.open(tarball_path, "w:gz") as tar:
            files = os.listdir(cfg.project_dir)
            for file in files:
                file_path = f"{cfg.project_dir}/{file}"
                if os.path.isdir(file_path):
                    if file in bwrap_ignore_dirs:
                        continue
                common.dbg(f"Compressing {file}")
                tar.add(file_path, filter=bwrap_exclude, arcname=file)
        common.info("Done")
        
    except Exception as e:
        common.fatal(f"Failed to create bubble-wrap tarball: {e}")



def bwrap_exclude(tar_info):
    for regex in bwrap_ignore_list:
        if tar_info.name.endswith(regex):
            return None
    return tar_info




def print_end_of_gen_image_message(ip, sim_job):
    if sim_job.dry_run:
        return
    if sim_job.target_name == "default":
        ip_str = f"{ip.name}"
    else:
        ip_str = f"{ip.name}"
        #ip_str = f"{ip.name}.{sim_job.target_name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    if sim_job.simulate:
        common.info("************************************************************************************************************************")
        common.info("* Compilation+Elaboration results: " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".log")
    else:
        common.info("************************************************************************************************************************")
        common.info("* Compilation+Elaboration results:")
        common.info("************************************************************************************************************************")
        common.info("  emacs " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".log &")
        common.info("  gvim  " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".log &")
        common.info("  vim   " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".log")
        common.info("")


def print_end_of_compilation_message(ip, sim_job):
    if sim_job.dry_run:
        return
    if sim_job.target_name == "default":
        ip_str = f"{ip.name}"
    else:
        ip_str = f"{ip.name}"
        #ip_str = f"{ip.name}.{sim_job.target_name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    if sim_job.simulate or sim_job.elaborate:
        common.info("************************************************************************************************************************")
        common.info("* Compilation results: " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".cmp.log")
    else:
        common.info("************************************************************************************************************************")
        common.info("* Compilation results:")
        common.info("************************************************************************************************************************")
        common.info("  emacs " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".cmp.log &")
        common.info("  gvim  " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".cmp.log &")
        common.info("  vim   " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".cmp.log")
        common.info("")


def print_end_of_elaboration_message(ip, sim_job):
    if sim_job.dry_run:
        return
    if sim_job.target_name == "default":
        ip_str = f"{ip.name}"
    else:
        ip_str = f"{ip.name}"
        #ip_str = f"{ip.name}.{sim_job.target_name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    if sim_job.simulate:
        common.info("************************************************************************************************************************")
        common.info("* Elaboration results: " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".elab.log")
    else:
        common.info("************************************************************************************************************************")
        common.info("* Elaboration results")
        common.info("************************************************************************************************************************")
        common.info("  emacs " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".elab.log &")
        common.info("  gvim  " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".elab.log &")
        common.info("  vim   " + cfg.sim_dir + "/cmp/" + ip_str + "." + sim_str + ".elab.log")
        common.info("")


def print_end_of_simulation_message(ip, sim_job):
    if sim_job.dry_run:
        return
    ip_str = f"{ip.vendor}/{ip.name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    results_path = sim_job.results_path
    common.info("************************************************************************************************************************")
    common.info("* Simulation results")
    common.info("************************************************************************************************************************")
    if (sim_job.waves):
        if sim_job.simulator == common.simulators_enum.VIVADO:
            common.info("* Waveforms: $MIO_VIVADO_HOME/xsim -gui " + results_path + "/waves.wdb &")
        elif sim_job.simulator == common.simulators_enum.VCS:
            common.info("* Waveforms: $MIO_VCS_HOME/dve -gui " + results_path + "/waves.wdb &")
        elif sim_job.simulator == common.simulators_enum.METRICS:
            common.info(f"* Waveforms: gtkwave {results_path}/waves.vcd &")
        elif sim_job.simulator == common.simulators_enum.XCELIUM:
            common.info("* Waveforms: $MIO_XCELIUM_HOME/simvision -gui " + results_path + "/waves.wdb &")
        elif sim_job.simulator == common.simulators_enum.QUESTA:
            common.info("* Waveforms: $MIO_QUESTA_HOME/visualizer -gui " + results_path + "/waves.wdb &")
        elif sim_job.simulator == common.simulators_enum.RIVIERA:
            common.info("* Waveforms: $MIO_RIVIERA_HOME/??? -gui " + results_path + "/waves.wdb &")
        common.info("")
    common.info("* Main log: emacs " + results_path + "/sim.log &")
    common.info("            gvim  " + results_path + "/sim.log &")
    common.info("            vim   " + results_path + "/sim.log")
    common.info("")
    common.info("* Test result dir: pushd " + results_path)
    common.info("* UVMx logs      : pushd " + results_path + "/uvmx_logs")
    common.info("")



def get_ip_cmp_est(ip, sim_job):
    ip_str = f"{ip.vendor}/{ip.name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    est_time = 0
    if ip_str in cfg.job_history:
        if 'compilation' in cfg.job_history[ip_str]:
            for job in cfg.job_history[ip_str]['compilation']:
                duration = job['duration']
                est_time += int(duration)
            est_time = math.ceil(est_time / len(cfg.job_history[ip_str]['compilation']))
    return est_time



def get_ip_elab_est(ip, sim_job):
    ip_str = f"{ip.vendor}/{ip.name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    est_time = 0
    if ip_str in cfg.job_history:
        if 'elaboration' in cfg.job_history[ip_str]:
            for job in cfg.job_history[ip_str]['elaboration']:
                duration = job['duration']
                est_time += int(duration)
            est_time = math.ceil(est_time / len(cfg.job_history[ip_str]['elaboration']))
    return est_time



def get_ip_gen_image_est(ip, sim_job):
    ip_str = f"{ip.vendor}/{ip.name}"
    sim_str = common.get_simulator_short_name(sim_job.simulator)
    est_time = 0
    if ip_str in cfg.job_history:
        if 'gen-image' in cfg.job_history[ip_str]:
            for job in cfg.job_history[ip_str]['gen-image']:
                duration = job['duration']
                est_time += int(duration)
            est_time = math.ceil(est_time / len(cfg.job_history[ip_str]['gen-image']))
    return est_time



def kill_progress_bar():
    global pbar
    if pbar:
        pbar.close()
atexit.register(kill_progress_bar)



def fill_progress_bar():
    global pbar
    global seconds_waited
    global est_time
    global overtime
    if pbar:
        pbar.update(est_time-seconds_waited)
        pbar.close()
        overtime = False



def progress_bar():
    global pbar
    global seconds_waited
    global est_time
    global overtime
    with tqdm(total=est_time, bar_format="{l_bar} {bar} {elapsed}<{remaining}") as pbar:
        for seconds_waited in range(est_time):
            time.sleep(1)
            pbar.update(1)
    if overtime:
        common.info(f"Job taking longer than average ({est_time} seconds)")



