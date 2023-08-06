# Copyright 2021-2023 Datum Technology Corporation
# SPDX-License-Identifier: GPL-3.0
########################################################################################################################


from mio import cache
from mio import common
from mio import cfg
from mio import clean
from mio import cov
from mio import dox
from mio import sim

import math
import json
import yaml
from yaml.loader import SafeLoader
import os
import jinja2
from jinja2 import Template
import xml.etree.cElementTree as ET
from datetime import datetime
import re


uvm_gen_dir = re.sub("results.py", "", os.path.realpath(__file__)) + ".."
relative_path_to_template = uvm_gen_dir + "/templates/"

interactive_html_report_template_path = relative_path_to_template + "interactive_results.html.j2"
regression_html_report_template_path  = relative_path_to_template + "regression_results.html.j2"


class Results:
    """results model"""

    def __init__(self, ip, name, is_regression, timestamp):
        self.name                        = name
        self.timestamp                   = timestamp
        self.is_regression               = is_regression
        self.simulator                   = ""
        self.regression_name             = ""
        self.regression_timestamp_start  = ""
        self.regression_timestamp_end    = ""
        self.regression_duration         = ""
        self.regression_duration_str     = ""
        self.default_test_suite          = True
        self.test_suite_name             = ""
        self.ip_str                      = ""
        self.ip_vendor                   = ip.vendor
        self.ip_name                     = ip.name
        self.target_name                 = ""
        self.has_target                  = False
        self.passed                      = False
        self.duration                    = 0
        self.duration_str                = ""
        self.num_tests                   = -1
        self.num_sets                    = -1
        self.num_groups                  = -1
        self.num_failed_tests            = -1
        self.num_passed_tests            = -1
        self.pct_passed                  = -1
        self.pct_failed                  = -1
        self.html_report_path            = ""
        self.xml_report_path             = ""
        self.failing_tests               = []
        self.sets                        = {}
    
    def add_set(self, set):
        set.results = self
        self.sets[set.name] = set
    
    def render(self):
        for set in self.sets:
            for group in self.sets[set].groups:
                for test in self.sets[set].groups[group].passing_tests:
                    test.render()
                for test in self.sets[set].groups[group].failing_tests:
                    test.render()
                    self.failing_tests.append(test)
                self.sets[set].groups[group].render()
            self.sets[set].render()
        
        self.num_sets = len(self.sets)
        self.duration = 0
        self.num_groups = 0
        self.num_tests = 0
        self.num_passed_tests = 0
        self.num_failed_tests = 0
        for set in self.sets:
            self.duration         += self.sets[set].duration
            self.num_groups       += self.sets[set].num_groups
            self.num_tests        += self.sets[set].num_tests
            self.num_passed_tests += self.sets[set].num_passed_tests
            self.num_failed_tests += self.sets[set].num_failed_tests
        self.pct_passed = int(self.num_passed_tests / (self.num_passed_tests + self.num_failed_tests) * 100)
        self.pct_failed = 100 - self.pct_passed
        if self.pct_passed == 100:
            self.passed = True
        if self.target_name != "default":
            has_target = True
        if self.is_regression and self.has_target:
            self.ip_str = f"{self.ip_name}#{self.target_name}"
        else:
            self.ip_str = f"{self.ip_name}"
        if self.is_regression:
            start = datetime.strptime(self.regression_timestamp_start, "%Y_%m_%d_%H_%M_%S")
            end   = datetime.strptime(self.regression_timestamp_end  , "%Y/%m/%d-%H:%M:%S")
            duration = end - start
            self.regression_duration = divmod(duration.seconds, 60)[1]
            self.regression_timestamp_start = start.strftime("%Y/%m/%d-%H:%M:%S")
            hours = math.floor(self.regression_duration / 3600)
            minutes = math.floor((self.regression_duration - (hours*3600)) / 60)
            seconds = math.ceil(self.regression_duration - (hours*3600) - (minutes*60))
            self.regression_duration_str = f"{str(hours)} hour(s), {str(minutes)} minute(s), {str(seconds)} second(s)"
        for set in self.sets:
            self.sets[set].duration_pct = int(self.sets[set].duration / self.duration * 100)
        hours = math.floor(self.duration / 3600)
        minutes = math.floor((self.duration - (hours*3600)) / 60)
        seconds = math.ceil(self.duration - (hours*3600) - (minutes*60))
        self.duration_str = f"{str(hours)} hour(s), {str(minutes)} minute(s), {str(seconds)} second(s)"


class TestSet:
    def __init__(self, name):
        self.name = name
        self.results = None
        self.duration = -1
        self.duration_pct = -1
        self.num_groups = -1
        self.num_tests = -1
        self.pct_passed = -1
        self.pct_failed = -1
        self.num_passed_tests = -1
        self.num_failed_tests = -1
        self.passed = False
        self.groups = {}
    
    def add_group(self, group):
        group.set = self
        self.groups[group.name] = group
    
    def render(self):
        self.num_groups = len(self.groups)
        self.duration = 0
        self.num_tests = 0
        self.num_passed_tests = 0
        self.num_failed_tests = 0
        for group in self.groups:
            self.duration         += self.groups[group].duration
            self.num_tests        += self.groups[group].num_tests
            self.num_passed_tests += self.groups[group].num_passed_tests
            self.num_failed_tests += self.groups[group].num_failed_tests
        self.pct_passed = int(self.num_passed_tests / (self.num_passed_tests + self.num_failed_tests) * 100)
        self.pct_failed = 100 - self.pct_passed
        if self.pct_passed == 100:
            self.passed = True
        for group in self.groups:
            self.groups[group].duration_pct = int(self.groups[group].duration / self.duration * 100)


class TestGroup:
    def __init__(self, name):
        self.name = name
        self.set = None
        self.duration = -1
        self.duration_pct = -1
        self.num_tests = -1
        self.pct_passed = -1
        self.pct_failed = -1
        self.num_passed_tests = -1
        self.num_failed_tests = -1
        self.passed = False
        self.passing_tests = []
        self.failing_tests = []
    
    def add_test(self, test):
        test.group = self
        test.set   = self.set
        if test.passed:
            self.passing_tests.append(test)
        else:
            self.failing_tests.append(test)
    
    def render(self):
        self.duration = 0
        self.num_passed_tests = len(self.passing_tests)
        self.num_failed_tests = len(self.failing_tests)
        self.num_tests  = self.num_passed_tests + self.num_failed_tests
        self.pct_passed = int(self.num_passed_tests / (self.num_passed_tests + self.num_failed_tests) * 100)
        self.pct_failed = 100 - self.pct_passed
        if self.pct_passed == 100:
            self.passed = True
        for test in self.passing_tests:
            self.duration += test.duration
        for test in self.failing_tests:
            self.duration += test.duration
        for test in self.passing_tests:
            test.duration_pct = int(test.duration / self.duration * 100)


class Test:
    def __init__(self, name, results_dir, results_path, sim_log_path, seed, duration):
        self.name         = name
        self.results_dir  = results_dir
        self.results_path = results_path
        self.sim_log_path = sim_log_path
        self.seed         = seed
        self.passed       = False
        self.conclusion   = ""
        self.duration     = duration
        self.duration_pct = -1
        self.num_errors   = -1
        self.num_warnings = -1
        self.set          = None
        self.group        = None
        self.args         = []
        self.errors       = []
        self.warnings     = []
        self.has_fatal    = False
        self.fatal        = ""
        self.notes        = []
    
    def add_arg(self, arg):
        self.args.append(arg)
    
    def add_error(self, text):
        self.errors.append(text)
    
    def add_warning(self, text):
        self.warnings.append(text)
    
    def add_note(self, text):
        self.notes.append(text)
    
    def render(self):
        self.num_errors   = len(self.errors  )
        self.num_warnings = len(self.warnings)


def interactive(ip_str, filename=""):
    vendor, name = common.parse_dep(ip_str)
    if vendor == "":
        ip = cache.get_anon_ip(name, True)
    else:
        ip = cache.get_ip(vendor, name, True)
    ip_str = f"{ip.vendor}/{ip.name}"
    timestamp = common.timestamp()
    results = Results(ip, filename, False, timestamp)
    test_set = TestSet("interactive")
    default_test_group = TestGroup("default")
    results.add_set(test_set)
    test_set.add_group(default_test_group)
    
    if ip_str in cfg.job_history:
        common.dbg(f"Parsing results for '{ip_str}'")
        if 'simulation' in cfg.job_history[ip_str]:
            for sim in cfg.job_history[ip_str]['simulation']:
                common.dbg("sim job history entry:\n" + str(sim))
                if (sim['type'] == "end") and (sim['is_regression'] == False):
                    sim_log_path = sim['log_path']
                    start = datetime.strptime(sim['timestamp_start'], "%Y/%m/%d-%H:%M:%S")
                    end   = datetime.strptime(sim['timestamp_end'  ], "%Y/%m/%d-%H:%M:%S")
                    duration = end - start
                    duration = divmod(duration.seconds, 60)[1]
                    new_test = Test(sim['test_name'], sim["dir_name"], sim["path"], sim_log_path, sim['seed'], duration)
                    
                    new_test.target_name = sim['target_name']
                    if sim['args'] != None:
                        for arg in sim['args']:
                            new_test.add_arg(arg)
                    new_test = parse_sim_log(results, sim_log_path, new_test)
                    if new_test.target_name == "default":
                        default_test_group.add_test(new_test)
                    else:
                        if new_test.target_name in test_set.groups:
                            test_set.groups[new_test.target_name].add_test(new_test)
                        else:
                            test_group = TestGroup(new_test.target_name)
                            test_set.add_group(test_group)
                            test_group.add_test(new_test)
    else:
        common.fatal(f"No simulation history for '{ip_str}'")
    
    results.render()
    if results.num_tests == 0:
        common.fatal("Did not find any test results")
    xml_file_path  = f"{cfg.sim_dir}/{filename}.xml"
    html_file_path = f"{cfg.sim_dir}/{filename}.html"
    gen_junit_xml(xml_file_path , results)
    gen_interactive_html_report(html_file_path, results)
    return results


def regression(input_filepath=""):
    tests_yml = None
    path = ""
    ip = None
    try:
        with open(input_filepath, 'r') as yamlfile:
            tests_yml = yaml.load(yamlfile, Loader=SafeLoader)
            if not tests_yml:
                raise Exception(f"tests.yml is empty")
            else:
                vendor = tests_yml['vendor']
                name   = tests_yml['ip']
                if vendor == "":
                    ip = cache.get_anon_ip(name, True)
                else:
                    ip = cache.get_ip(vendor, name, True)
                ip_str = f"{ip.vendor}/{ip.name}"
                filename = f""
                path = tests_yml['path']
                results = Results(ip, tests_yml['regression_name'], True, tests_yml['timestamp_start'])
                results.regression_name            = tests_yml['regression_name']
                results.regression_timestamp_start = tests_yml['timestamp_start']
                results.regression_timestamp_end   = tests_yml['timestamp_end']
                results.target_name                = tests_yml['target_name']
                results.test_suite_name            = tests_yml['test_suite_name']
                results.simulator                  = tests_yml['simulator']
                
                if results.target_name != "default":
                    results.has_target = True
                
                for test in tests_yml['tests']:
                    td = tests_yml['tests'][test]
                    start = datetime.strptime(td['timestamp_start'], "%Y/%m/%d-%H:%M:%S")
                    end   = datetime.strptime(td['timestamp_end'  ], "%Y/%m/%d-%H:%M:%S")
                    duration = end - start
                    duration = divmod(duration.seconds, 60)[1]
                    new_test = Test(td['name'], td['results_dir_name'], td['results_path'], td['sim_log_file_path'], td['seed'], duration)
                    for arg in td['args']:
                        new_test.add_arg(arg)
                    new_test = parse_sim_log(results, td['sim_log_file_path'], new_test)
                    set = td['set']
                    group = td['test_group']
                    if set not in results.sets:
                        new_set = TestSet(set)
                        results.add_set(new_set)
                    if group not in results.sets[set].groups:
                        new_group = TestGroup(group)
                        results.sets[set].add_group(new_group)
                    results.sets[set].groups[group].add_test(new_test)
    except Exception as e:
        common.fatal(f"Failed to parse regression results: {e}")
    
    results.render()
    if results.num_tests == 0:
        common.fatal("Did not find any test results")
    
    if results.has_target:
        filename = f"{ip.name}_{results.target_name}_{results.regression_name}"
    else:
        filename = f"{ip.name}_{results.regression_name}"
    
    xml_file_path  = f"{path}/{filename}.xml"
    html_file_path = f"{path}/{filename}.html"
    gen_junit_xml(xml_file_path , results)
    gen_regression_html_report(html_file_path, results)
    return results


def parse_sim_log(results, sim_log_path, test):
    sim_str = common.get_simulator_short_name(results.simulator)
    if not os.path.exists(sim_log_path):
        test.fatal = True
        test.passed = False
        test.add_note("No simulation log file")
        test.conclusion = "NO LOG!"
        return test
    
    for i, line in enumerate(open(sim_log_path)):
        for regex in cfg.warning_regexes:
            matches = re.search(regex, line)
            if matches:
                test.add_warning(matches.group(0))
        for regex in cfg.error_regexes:
            matches = re.search(regex, line)
            if matches:
                test.add_error(matches.group(0))
                test.passed = False
                test.conclusion = "FAILED"
        for regex in cfg.fatal_regexes:
            matches = re.search(regex, line)
            if matches:
                test.has_fatal = True
                test.fatal = matches.group(0)
                test.passed = False
                test.add_note("Has simulation fatal error")
                test.conclusion = "FATAL"
                break
        if sim_str == common.simulators_enum.VIVADO:
            for string in cfg.viv_fatal_errors:
                if string in line:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has vivado fatal error")
                    test.conclusion = "FATAL"
                    break
        if sim_str == common.simulators_enum.METRICS:
            for string in cfg.mdc_fatal_errors:
                if matches:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has dsim fatal error")
                    test.conclusion = "FATAL"
                    break
        if sim_str == common.simulators_enum.VCS:
            for string in cfg.vcs_fatal_errors:
                if matches:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has vcs fatal error")
                    test.conclusion = "FATAL"
                    break
        if sim_str == common.simulators_enum.QUESTA:
            for string in cfg.qst_fatal_errors:
                if matches:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has questa fatal error")
                    test.conclusion = "FATAL"
                    break
        if sim_str == common.simulators_enum.XCELIUM:
            for string in cfg.xcl_fatal_errors:
                if matches:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has xcelium fatal error")
                    test.conclusion = "FATAL"
                    break
        if sim_str == common.simulators_enum.RIVIERA:
            for string in cfg.riv_fatal_errors:
                if matches:
                    test.has_fatal = True
                    test.fatal = line
                    test.passed = False
                    test.add_note("Has riviera-pro fatal error")
                    test.conclusion = "FATAL"
                    break
    if test.conclusion != "FATAL":
        if len(test.errors) > 0:
            test.conclusion = "FAILED"
        else:
            test.conclusion = "PASSED"
            test.passed = True
    return test


def gen_junit_xml(filepath, results):
    group_count = 0
    testsuites = ET.Element("testsuites")
    testsuites.set('id', f"{results.ip_str}_{results.name}")
    testsuites.set('name', results.ip_str)
    testsuites.set('tests', str(results.num_tests))
    testsuites.set('failures', str(results.num_failed_tests))
    if results.is_regression:
        testsuites.set('time', str(results.regression_duration))
    else:
        testsuites.set('time', str(results.duration))
    
    for set in results.sets:
        cur_set = results.sets[set]
        for group in cur_set.groups:
            cur_group = cur_set.groups[group]
            testsuite = ET.SubElement(testsuites, "testsuite")
            testsuite.set('id', str(group_count))
            testsuite.set('name', f"{cur_set.name}.{cur_group.name}")
            testsuite.set('tests', str(cur_group.num_tests))
            testsuite.set('failures', str(cur_group.num_failed_tests))
            testsuite.set('time', str(cur_group.duration))
            for test in cur_group.failing_tests:
                testcase = ET.SubElement(testsuite, "testcase")
                testcase.set('id', test.results_dir)
                testcase.set('name', test.results_dir)
                testcase.set('time', str(test.duration))
                for error in test.errors:
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", error)
                    failure.set("type", "ERROR")
                if test.has_fatal:
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", test.fatal)
                    failure.set("type", "FATAL")
            for test in cur_group.passing_tests:
                testcase = ET.SubElement(testsuite, "testcase")
                testcase.set('id', test.results_dir)
                testcase.set('name', test.results_dir)
                testcase.set('time', str(test.duration))
            group_count += 1
    tree = ET.ElementTree(testsuites)
    try:
        tree.write(filepath)
    except Exception as e:
        common.fatal("Failed to write xml report to disk: " + str(e))
    common.dbg(f"Wrote {filepath}")
    results.xml_report_path = filepath


def gen_interactive_html_report(filepath, results):
    try:
        fin = open(interactive_html_report_template_path, "r")
        template_data = fin.read()
        html_report_template = Template(template_data)
        html_report_contents = html_report_template.render(results=results)
        with open(filepath,'w') as htmlfile:
            htmlfile.write(html_report_contents)
        htmlfile.close()
        common.dbg(f"Wrote {filepath}")
        results.html_report_path = filepath
    except Exception as e:
        common.fatal("Failed to write html report to disk: " + str(e))


def gen_regression_html_report(filepath, results):
    try:
        fin = open(regression_html_report_template_path, "r")
        template_data = fin.read()
        html_report_template = Template(template_data)
        html_report_contents = html_report_template.render(results=results)
        with open(filepath,'w') as htmlfile:
            htmlfile.write(html_report_contents)
        htmlfile.close()
        common.dbg(f"Wrote {filepath}")
        results.html_report_path = filepath
    except Exception as e:
        common.fatal("Failed to write html report to disk: " + str(e))
