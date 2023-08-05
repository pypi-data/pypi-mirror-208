#!/usr/bin/env python3

"""
This script simply wraps terragrunt (which is a wrapper around terraform...)
and its main function is to allow you to execute a `run-all` command but
broken up in individual steps.

This makes debugging a complex project easier, such as spotting where the
exact problem is.
"""

# idea: parse output
# - https://github.com/bcochofel/terraplanfeed/tree/main/terraplanfeed

import os
import sys
import subprocess
import shlex
import shutil
import glob
import re
import tempfile
import json
import yaml
import threading
import queue
import multiprocessing
import click
import networkx as nx

from .printer import Printer
from .terrasafe import run_terrasafe

class TgWrap():
    """
    A wrapper around terragrunt with the sole purpose to make it a bit
    (in an opiionated way) easier to use
    """
    SEPARATOR=':|:'

    def __init__(self, verbose):
        self.printer = Printer(verbose)

        # Check if the "TERRAGRUNT_SOURCE" environment variable is set
        env_var = "TERRAGRUNT_SOURCE"
        if env_var in os.environ:
            self.printer.warning(
                f"'{env_var}' environment variable is set with address: '{os.environ[env_var]}'!"
                )
        else:
            self.printer.success(
                f"No '{env_var}' variable is set, so the sources as defined in terragrunt.hcl files will be used as is!"
                )

    def _is_installed(self, program):
        """ Checks if a program is installed on the system """
        return shutil.which(program) is not None

    def load_yaml_file(self, filepath):
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)

    def _construct_command(self, command, debug, exclude_external_dependencies,
        non_interactive=True, no_auto_approve=True, no_lock=True, update=False,
        planfile=None, working_dir=None, limit_parallelism=None, 
        include_dir=[], exclude_dir=[], terragrunt_args=()):
        """ Constructs the command """

        PLANFILE_NAME="planfile"

        commands = {
            'generic': '{base_command} {command} --terragrunt-non-interactive {no_auto_approve} {update} {parallelism} {common}',
            'info': '{base_command} terragrunt-info --terragrunt-non-interactive {update} {common}',
            'plan': '{base_command} {command} --terragrunt-non-interactive  -out={planfile_name} {lock_level} {update} {parallelism} {common}',
            'apply': '{base_command} {command} {non_interactive} {no_auto_approve} {update} {parallelism} {common} {planfile}',
            'show': '{base_command} {command} --terragrunt-non-interactive {ignore_deps} {update} -json {planfile_name}', # no working dir allowed here!!!
            'destroy': '{base_command} {command} {non_interactive} {no_auto_approve} {parallelism} {common} {planfile}',
        }

        lock_stmt         = '-lock=false' if no_lock else ''
        update_stmt       = '--terragrunt-source-update' if update else ''
        ignore_deps_stmt  = '--terragrunt-ignore-external-dependencies' if exclude_external_dependencies else '--terragrunt-include-external-dependencies'
        debug_stmt        = '--terragrunt-log-level debug --terragrunt-debug' if debug else ''
        auto_approve_stmt = '--terragrunt-no-auto-approve' if no_auto_approve else ''
        interactive_stmt  = '--terragrunt-non-interactive' if non_interactive else ''
        working_dir_stmt  = f'--terragrunt-working-dir {working_dir}' if working_dir else ''
        parallelism_stmt  = f'--terragrunt-parallelism {limit_parallelism}' if limit_parallelism else ''
        planfile_stmt     = f'{PLANFILE_NAME}' if planfile else ''
        include_dir_stmt  = f'--terragrunt-strict-include  --terragrunt-include-dir {" --terragrunt-include-dir ".join(include_dir)}' if len(include_dir) > 0 else ""
        exclude_dir_stmt  = f'--terragrunt-exclude-dir {" --terragrunt-exclude-dir ".join(exclude_dir)}' if len(exclude_dir) > 0 else ""

        base_command      = 'terragrunt run-all'
        common_commands = f"{ignore_deps_stmt} {debug_stmt} {working_dir_stmt} {include_dir_stmt} {exclude_dir_stmt} {' '.join(terragrunt_args)}"

        # if we are using an 'init' together with update, add the `-upgrade` as well
        if command.lower() == 'init' and update:
            update_stmt       = '--terragrunt-source-update -upgrade'

        if command not in ['clean']:
            full_command = commands.get(command, commands.get('generic')).format(
                base_command=base_command,
                command=command,
                lock_level=lock_stmt,
                update=update_stmt,
                ignore_deps=ignore_deps_stmt,
                no_auto_approve=auto_approve_stmt,
                non_interactive=interactive_stmt,
                parallelism=parallelism_stmt,
                planfile=planfile_stmt,
                common=common_commands,
                planfile_name=PLANFILE_NAME,
            )
        else:
            full_command = commands.get(command, commands.get('generic'))

        # remove double spaces
        full_command = re.sub(' +', ' ', full_command)

        self.printer.verbose(f'Full command to execute:\n$ {full_command}')

        return full_command

    def _prepare_groups(self, graph, exclude_external_dependencies, working_dir,
                        exclude_dir=[], include_dir=[]):
        """ Prepare the list of groups that will be executed """

        working_dir = os.path.abspath(working_dir) if working_dir else os.getcwd()
        self.printer.verbose(f"Check for working dir: {working_dir}")

        # ensure consistency, remove possible trailing slashes from the dirs
        exclude_dir = [dir.rstrip(os.path.sep) for dir in exclude_dir]
        include_dir = [dir.rstrip(os.path.sep) for dir in include_dir]

        self.printer.verbose(f"Include dirs: {'; '.join(include_dir)}")
        self.printer.verbose(f"Exclude dirs: {'; '.join(exclude_dir)}")

        groups = []
        for group in nx.topological_generations(graph):
            try:
                group.remove("\\n") # terragrunt is adding this in some groups for whatever reason
            except ValueError:
                pass

            for idx, directory in enumerate(group):
                dir_excluded = False
                dir_included = True if len(include_dir) == 0 else False
                dir_excluded_reason = ""

                # ensure consistency, remove possible trailing slashes from the dirs                
                directory = directory.rstrip(os.path.sep)

                common_path = os.path.commonpath([working_dir, os.path.abspath(directory)])
                # self.printer.verbose(f'Common path for dir {directory}: {common_path}')
                if common_path != working_dir \
                    and exclude_external_dependencies:
                    dir_excluded = True
                    dir_excluded_reason = "directory out of scope"

                for i in exclude_dir:
                    exclude_paths = glob.glob(i)
                    if directory in exclude_paths:
                        dir_excluded = True
                        dir_excluded_reason = "directory explicitly excluded"

                # if we have a specific set of include_dirs, then everything else should be excluded
                for i in include_dir:
                    include_paths = glob.glob(i)
                    if directory in include_paths:
                        dir_included = True

                if dir_excluded:
                    self.printer.verbose(
                        f"- Remove directory '{directory}' from group: {dir_excluded_reason}"
                        )
                    group[idx] = None
                elif not dir_included:
                    self.printer.verbose(
                        f"- Remove directory '{directory}' from group: specific list of include dirs given"
                        )
                    group[idx] = None
                else:
                    self.printer.verbose(f"+ Include directory: {directory}")

            # remove the null values from the list
            group = list(filter(None, group))
            if len(group) > 0:
                groups.append(group)

        return groups

    def _get_di_graph(self, backwards=False, working_dir=None):
        """ Gets the directed graph of terragrunt dependencies, and parse it into a graph object """
        graph = None
        try:
            f = tempfile.NamedTemporaryFile(mode='w+', prefix='tgwrap-', delete=True)
            self.printer.verbose(f"Opened temp file for graph collection: {f.name}")

            working_dir_stmt = f'--terragrunt-working-dir {working_dir}' if working_dir else ''
            command = \
                f'terragrunt graph-dependencies --terragrunt-non-interactive {working_dir_stmt}'
            rc = subprocess.run(
                shlex.split(command),
                text=True,
                stdout=f,
            )
            self.printer.verbose(rc)

            f.flush()

            graph = nx.DiGraph(nx.nx_pydot.read_dot(f.name))
            if not backwards:
                # For regular operations the graph must be reversed
                graph = graph.reverse()
            else:
                self.printer.verbose("Graph will be interpreted backwards!")
        except TypeError as e:
            self.printer.error('terragrunt has problems generating the graph, check the dependencies please!')
            self.printer.error("once fixed, you can run 'tgwrap show-graph' to verify.")
            raise click.ClickException(e)
        except Exception as e:
            self.printer.error(e)
            raise click.ClickException(e)
        finally:
            f.close()

        return graph

    def _analyze_results(self, rc, messages):
        """ Checks for errors """

        error = False
        skip = False

        messages = messages.lower()

        if rc.returncode != 0 or 'error' in messages.lower():
            error = True

        if 'skipping terragrunt module' in messages.lower():
            skip = True

        return error, skip

    def _run_graph_step(self, command, working_dir, module, collect_output_file, dry_run, progress, 
        output_queue=None, semaphore=None):
        """ Runs a step in the graph """

        MODULE_IDENTIFIER=f'{module}{self.SEPARATOR}'

        stop_processing = False
        error = False
        skip = False
        output = None
        error_msg = None

        try:
            # if we are in multi-threading mode, acquire a semaphore
            if semaphore:
                semaphore.acquire()

            # if we have a specific working dir, and the dir is relative, combine the two
            if working_dir and not os.path.isabs(module):
                module = os.path.join(os.path.abspath(working_dir), module)
                self.printer.verbose(f'Executing in directory: {working_dir}')

            self.printer.header(
                f'\n\nStart processing module: {module} ({progress})\n\n',
                print_line_before=True,
                )

            if dry_run:
                self.printer.warning(
                    'In dry run mode, no real actions are executed!!'
                    )
            else:
                if collect_output_file:
                    self.printer.verbose('Use an output file for output collection')

                    # module identifier needs to be pre-written to output file, so that the output can be appended to it
                    collect_output_file.write(MODULE_IDENTIFIER)
                    collect_output_file.flush()
                elif output_queue:
                    self.printer.verbose('Use an output queue for output collection')

                    # no output file, but data must be written to queue
                    # so we need to capture the output
                    collect_output_file = subprocess.PIPE

                messages = ""

                with tempfile.NamedTemporaryFile(mode='w+', prefix='tgwrap-', delete=False) as f:
                    self.printer.verbose(f"Opened temp file for error collection: {f.name}")
                    rc = {'returncode': 0}
                    rc = subprocess.run(
                        shlex.split(command),
                        text=True,
                        cwd=module,
                        stdout=collect_output_file if collect_output_file else sys.stdout,
                        stderr=f,
                    )

                    self.printer.verbose(f'arguments: {rc.args}')
                    self.printer.verbose(f'returncode: {rc.returncode}')
                    try:
                        self.printer.verbose(f'stdout: {rc.stdout[:200]}')
                    except Exception:
                        pass

                with open(f.name, 'r') as f:
                    messages = f.read()

                error, skip = self._analyze_results(
                    rc=rc,
                    messages=messages,
                    )
                
                # if we have a skipped module, and are collecting output, make sure we end up on a new line

                output = rc.stdout if rc.stdout else '\n'

                if skip:
                    self.printer.verbose("Module is skipped")

                if error:
                    raise Exception(
                        f'An error situation detected while processing the terragrunt dependencies graph in directory {module}'
                    )
                else:
                    self.printer.success(
                        f'Directory {module} processed successfully',
                    )

        except FileNotFoundError:
            error_msg = f'Directory {module} not found, continue'
            self.printer.warning(error_msg)
        except Exception as e:
            error_msg = f"Error occurred:\n{str(e)}"
            self.printer.error(error_msg)
            self.printer.error("Full stack:", print_line_before=True)
            self.printer.normal(messages, print_line_after=True)
            self.printer.normal(f"Directory {module} failed!")

            stop_processing = True
        finally:
            if error_msg:
                # output = f'{{"exception": "{error_msg}"}}'
                output = json.dumps({"exception": error_msg})

            try:
                # communicate the results if desired
                if output_queue:
                    output_queue.put(f'{MODULE_IDENTIFIER}{output}')
                elif collect_output_file and (skip or error):
                    collect_output_file.write(output)
                    collect_output_file.flush()
            except Exception as e:
                self.printer.error(f'Error writing the results: {e}')

            if semaphore:
                semaphore.release()
            try:
                os.remove(f.name)
            except Exception:
                pass

        return stop_processing

    def _run_di_graph(
        self, command, exclude_external_dependencies, start_at_step, dry_run,
        parallel_execution=False, ask_for_confirmation=False, collect_output_file=None,
        backwards=False, working_dir=None, include_dir=[], exclude_dir=[], 
        ):
        "Runs the desired command in the directories as defined in the directed graph"

        graph = self._get_di_graph(backwards=backwards, working_dir=working_dir)

        # first go through the groups and clean up where needed
        groups = self._prepare_groups(
            graph=graph,
            exclude_external_dependencies=exclude_external_dependencies,
            working_dir=working_dir,
            include_dir=include_dir,
            exclude_dir=exclude_dir,
            )

        if not groups:
            self.printer.error('No groups to process, this smells fishy!')
        elif ask_for_confirmation or self.printer.verbose:
            self.printer.header("The following groups will be processed:")
            for idx, group in enumerate(groups):
                self.printer.normal(f"\nGroup {idx+1}:")
                for module in group:
                    self.printer.normal(f"- {module}")

        if ask_for_confirmation:
            response = input("\nDo you want to continue? (y/n) ")
            if response.lower() != "y":
                sys.exit(1)

        # We only support multi-threading with 'show'
        nbr_of_threads = multiprocessing.cpu_count() if parallel_execution and 'show' in command.lower() else 1

        if parallel_execution:
            self.printer.warning(f'We are in EXPERIMENTAL multi-threading mode using {nbr_of_threads} threads!')
            q = queue.Queue()
            semaphore = threading.Semaphore(nbr_of_threads)
            threads = []

        counter = 0
        nbr_of_groups = len(groups)
        for idx, group in enumerate(groups):
            group_nbr=idx+1
            self.printer.header(f'Group {group_nbr}')
            self.printer.normal(group)

            nbr_of_modules = len(group)
            for idx2, module in enumerate(group):
                counter += 1
                module_nbr=idx2+1
                progress = f'module {module_nbr} (of {nbr_of_modules}) of group {group_nbr} (of {nbr_of_groups})'

                step_nbr = group_nbr + module_nbr/100
                if step_nbr < start_at_step:
                    self.printer.normal(f'Skip step {step_nbr}, start at {start_at_step}')
                    continue

                if parallel_execution:
                    self.printer.verbose(f'Start thread #{counter} for step {step_nbr}')
                    t = threading.Thread(
                        target=self._run_graph_step,
                        kwargs={
                            "command": command,
                            "working_dir": working_dir,
                            "module": module,
                            "collect_output_file": None, # in parallel mode we can't write directly to the output file
                            "dry_run": dry_run,
                            "progress": progress,
                            "output_queue": q,
                            "semaphore": semaphore,
                            }
                        )
                    t.start()
                    threads.append(t)
                else:
                    stop_processing = self._run_graph_step(
                        command=command,
                        working_dir=working_dir,
                        module=module,
                        collect_output_file=collect_output_file,
                        dry_run=dry_run,
                        progress=progress,
                    )

                    if stop_processing:
                        self.printer.warning(f"Processing needs to be stopped at step {step_nbr}.")
                        self.printer.normal(
                            f"After you've fixed the problem, you can continue where you left off by adding '--start-at-step {step_nbr}'."
                            )
                        sys.exit(1)

        if parallel_execution:
            # now wait until the threads are done and collect the output
            # todo: how to implement something as stop_processing like in regular execution?
            total_counter = counter
            counter = 0
            for t in threads:
                counter += 1
                self.printer.verbose(f'Wait for thread #{counter} (of {total_counter}) to finish')
                t.join()
                collect_output_file.write(q.get())
        
        self.printer.verbose(f'Executed {group_nbr} groups and {step_nbr} steps')

    def _run_sync(
        self, source_path, target_path, auto_approve, include_lock_file, dry_run, clean_up,
        excludes=[], source_stage=None, target_stage=None, source_domain=None,
        ):
        """ Run a sync copying files from a source to a target path """

        if not self._is_installed('rsync'):
            self.printer.error("'rsync' seems not installed. Cannot continue")
        elif not os.path.exists(source_path):
            self.printer.error(f"Cannot find {source_path}. Cannot continue.")
            if source_domain:
                self.printer.error(
                    "Please ensure you are in the directory that contains your projects, " + \
                    "or use --working-dir option"
                )
            else:
                self.printer.error(
                    "Please ensure you are in the root of your project, or use --working-dir option"
                )
        else:
            self.printer.verbose(f"Copying config: {source_path} => {target_path}")

            try:
                os.makedirs(target_path)
            except OSError:
                # directory already exists
                pass

            dry_run_stmt = '--dry-run' if dry_run else ''
            clean_stmt   = '--delete' if clean_up else ''
            env_file_stmt   = "--exclude='env.hcl'" if source_stage != target_stage else "--include='env.hcl'"
            lock_file_stmt  = "--include='.terraform.lock.hcl'" if include_lock_file \
                else "--exclude='.terraform.lock.hcl'"
            excludes_stmt = ' '.join([f"--exclude={x}" for x in excludes])

            cmd = f"rsync -aim {dry_run_stmt} {clean_stmt} " + \
                f"--include='terragrunt.hcl' {lock_file_stmt} {env_file_stmt} {excludes_stmt} " + \
                "--exclude='.terragrunt-cache/' --exclude='.terraform/' " + \
                "--exclude='terragrunt-debug.tfvars.json' --exclude=planfile " + \
                "--exclude='.DS_Store' " + \
                f"{source_path} {target_path}"

            cmd = re.sub(' +', ' ', cmd)

            self.printer.header("Will be deploying:", print_line_before=True)
            self.printer.normal(f"from: {source_path}")
            self.printer.normal(f"to:   {target_path}")
            self.printer.verbose(f"Using command:\n$ {cmd}")

            if not auto_approve:
                response = input("\nDo you want to continue? (y/n) ")
                if response.lower() != "y":
                    sys.exit(1)

            rc = subprocess.run(shlex.split(cmd))
            self.printer.verbose(rc)

    def run(self, command, debug, dry_run, no_lock, update,
        planfile, auto_approve, working_dir, terragrunt_args):
        """ Executes a terragrunt command on a single module """

        self.printer.verbose(f"Attempting to execute 'run {command}'")
        if terragrunt_args:
            self.printer.verbose(f"- with additional parameters: {' '.join(terragrunt_args)}")

        check_for_file="terragrunt.hcl"
        if working_dir:
            check_for_file = os.path.join(working_dir, check_for_file)
        if not os.path.isfile(check_for_file):
            self.printer.error(
                f"{check_for_file} not found, this seems not to be a terragrunt module directory!"
                )
            sys.exit(1)

        cmd = self._construct_command(
            command=command,
            debug=debug,
            exclude_external_dependencies=True,
            no_lock=no_lock,
            update=update,
            planfile=planfile,
            no_auto_approve=(not auto_approve),
            working_dir=working_dir,
            terragrunt_args=terragrunt_args,
        )

        if dry_run:
            self.printer.warning(f'In dry run mode, no real actions are executed!!')
        else:
            # the `posix=False` is to prevent the split command to remove quotes from strings,
            # e.g. when executing commands like this:
            # tgwrap state mv 'azuread_group.this["viewers"]' 'azuread_group.this["readers"]'
            rc = subprocess.run(shlex.split(cmd, posix=False))
            self.printer.verbose(rc)

    def run_all(self, command, debug, dry_run, no_lock, update,
        exclude_external_dependencies, step_by_step, planfile, auto_approve, 
        working_dir, start_at_step, limit_parallelism, include_dir, exclude_dir, terragrunt_args):
        """ Executes a terragrunt command across multiple modules """

        self.printer.verbose(f"Attempting to execute 'run-all {command}'")
        if terragrunt_args:
            self.printer.verbose(f"- with additional parameters: {' '.join(terragrunt_args)}")

        # auto approve is only relevant with a modifying command
        modifying_command = (command.lower() in ['apply', 'destroy'])
        auto_approve = auto_approve if modifying_command else True

        cmd = self._construct_command(
            command=command,
            debug=debug,
            exclude_external_dependencies=True if step_by_step else exclude_external_dependencies,
            non_interactive=True if step_by_step else auto_approve,
            no_lock=no_lock,
            update=update,
            planfile=planfile,
            no_auto_approve=False if step_by_step else (not auto_approve),
            working_dir=None if step_by_step else working_dir,
            terragrunt_args=terragrunt_args,
            limit_parallelism=limit_parallelism,
            include_dir=[] if step_by_step else include_dir,
            exclude_dir=[] if step_by_step else exclude_dir,
        )

        if step_by_step:
            self.printer.verbose(
                f'This command will be executed for each individual module:\n$ {cmd}'
                )

            self._run_di_graph(
                command=cmd,
                exclude_external_dependencies=exclude_external_dependencies,
                working_dir=working_dir,
                ask_for_confirmation=(not auto_approve),
                dry_run=dry_run,
                start_at_step=start_at_step,
                backwards=True if command.lower() in ['destroy'] else False,
                include_dir=include_dir,
                exclude_dir=exclude_dir,
            )
        else:
            if dry_run:
                self.printer.warning('In dry run mode, no real actions are executed!!')
            else:
                rc = subprocess.run(shlex.split(cmd))
                self.printer.verbose(rc)

    def run_import(self, address, id, dry_run, working_dir, no_lock, terragrunt_args):
        """ Executes the terragrunt/terraform import command """

        self.printer.verbose(f"Attempting to execute 'run import'")
        if terragrunt_args:
            self.printer.verbose(f"- with additional parameters: {' '.join(terragrunt_args)}")

        check_for_file="terragrunt.hcl"
        if working_dir:
            check_for_file = os.path.join(working_dir, check_for_file)
        if not os.path.isfile(check_for_file):
            self.printer.error(
                f"{check_for_file} not found, this seems not to be a terragrunt module directory!"
                )
            sys.exit(1)

        lock_stmt         = '-lock=false' if no_lock else ''
        working_dir_stmt  = f'--terragrunt-working-dir {working_dir}' if working_dir else ''

        cmd = f"terragrunt import {working_dir_stmt} {lock_stmt} {address} {id} {' '.join(terragrunt_args)}"
        cmd = re.sub(' +', ' ', cmd)
        self.printer.verbose(f'Full command to execute:\n$ {cmd}')

        if dry_run:
            self.printer.warning(f'In dry run mode, no real actions are executed!!')
        else:
            env = os.environ.copy()
            # TERRAGRUNT_SOURCE should not be present (or it should be a fully qualified path (which is typically not the case))
            try:
                value = env.pop('TERRAGRUNT_SOURCE')
                if value:
                    self.printer.verbose(
                        f'Terragrunt source environment variable with value {value} will be ignored'
                        )
            except KeyError:
                pass

            # the `posix=False` is to prevent the split command to remove quotes from strings,
            # e.g. when executing commands like this:
            # tgwrap import 'azuread_group.this["viewers"]' '123e4567-e89b-12d3-a456-426655440000'
            rc = subprocess.run(
                shlex.split(cmd, posix=False),
                env=env,
            )
            self.printer.verbose(rc)

    def analyze(self, dry_run, exclude_external_dependencies, working_dir, start_at_step,
        out, terrasafe_config, parallel_execution, include_dir, exclude_dir, terragrunt_args):
        """ Analyzes the plan files """

        self.printer.verbose("Attempting to 'analyze'")
        if terragrunt_args:
            self.printer.verbose(f"- with additional parameters: {' '.join(terragrunt_args)}")

        # first run a 'show' and write output to file
        cmd = self._construct_command(
            command='show',
            exclude_external_dependencies=True,
            debug=False,
            terragrunt_args=terragrunt_args,
            )

        ts_config = None
        if not terrasafe_config:
            self.printer.warning(
                f"Terrasafe config file is not set, this is required for running the terrasafe command!"
                )
        else:
            self.printer.verbose(
                f"\nRun terrasafe using config {terrasafe_config}"
                )

            with open(terrasafe_config) as f:
                ts_config = json.load(f)

        ts_validation_successful = True
        changes = {}
        try:
            # then run it and capture the output
            with tempfile.NamedTemporaryFile(mode='w+', prefix='tgwrap-', delete=False) as f:
                self.printer.verbose(f"Opened temp file for output collection: {f.name}")

                self._run_di_graph(
                    command=cmd,
                    exclude_external_dependencies=exclude_external_dependencies,
                    dry_run=dry_run,
                    collect_output_file=f,
                    working_dir=working_dir,
                    start_at_step=start_at_step,
                    ask_for_confirmation=False,
                    include_dir=include_dir,
                    exclude_dir=exclude_dir,
                    parallel_execution=parallel_execution,
                )

            with open(f.name, 'r') as f:
                for line in f:
                    split_line = line.split(self.SEPARATOR)
                    module = split_line[0]
                    try:
                        plan_file = split_line[1]
                    except IndexError:
                        self.printer.warning(f'Could not determine planfile: {line[:100]}')

                    changes[module] = {
                        "deletions" : [],
                        "other" : [],
                        "unauthorized" : [],
                    }

                    try:
                        # plan file could be empty (except for new line) if module is skipped
                        if len(plan_file) > 1:
                            data = json.loads(plan_file)

                            # check for unauthorized deletions
                            if ts_config:
                                changes[module]["unauthorized"] = run_terrasafe(
                                    config=ts_config,
                                    data=data,
                                    verbose=self.printer.print_verbose,
                                    )
                                if len(changes[module]["unauthorized"]) > 0:
                                    ts_validation_successful = False

                            # do we have an exception logged?
                            if 'exception' in data:
                                raise Exception(data['exception'])
                            elif len(data.get('resource_changes', [])) > 0:
                                for rc in data['resource_changes']:
                                    # check if we do have actual changes
                                    actions = rc['change']['actions']
                                    action = f'{rc["address"]}: {", ".join(actions)}'
                                    if len(actions) == 1 and (actions[0] == 'no-op' or actions[0] == 'read'):
                                        pass # ignore, just an state change
                                    elif 'delete' in actions:
                                        # only include if it is not already included in the unauthorized section
                                        if action.split(":")[0] not in changes[module]["unauthorized"]:
                                            changes[module]["deletions"].append(action)
                                    else:
                                        changes[module]["other"].append(action)
                        else:
                            self.printer.warning(f'Planfile for module {module} is empty')
                    except json.decoder.JSONDecodeError as e:
                        raise Exception(
                            f"Exception detected or planfile for {module} was not proper json, further analysis not possible:\n{plan_file[:200]}"
                            ) from e
        finally:
            os.remove(f.name)

        self.printer.header("Analysis results:", print_line_before=True)
        for key, value in changes.items():
            self.printer.header(f'Module: {key}')
            if not (value["deletions"] or value["other"] or value["unauthorized"]):
                self.printer.success('- No changes detected')
            if value["unauthorized"]:
                self.printer.error('- Unauthorized deletions:')
                for m in value["unauthorized"]:
                    self.printer.error(f' -> {m}')
            if value["deletions"]:
                self.printer.warning('- Deletions:')
                for m in value["deletions"]:
                    self.printer.warning(f' -> {m}')
            if value["other"]:
                self.printer.normal('- Other:')
                for m in value["other"]:
                    self.printer.normal(f' -> {m}')

        if out:
            print(json.dumps(changes, indent=4))

        if not ts_validation_successful:
            self.printer.error("Terrasafe validation failed on one or more modules")
            sys.exit(1)

    def set_lock(self, module, lock_status, auto_approve, dry_run, working_dir):
        """ Set the lock status of the stage you're in """
    
        # do we have a working dir?
        working_dir = working_dir if working_dir else os.getcwd()
        module_path = os.path.join(working_dir, module)

        command = "destroy" if lock_status == "unlock" else "apply" 

        self.run(
            command=command,
            dry_run=dry_run,
            auto_approve=auto_approve,
            working_dir=module_path,
            debug=False,
            no_lock=False,
            update=False,
            planfile=None,
            terragrunt_args=[],
            )

    def sync(
        self, source_stage, target_stage, source_domain, target_domain, module,
        auto_approve, dry_run, clean_up, include_lock_file, working_dir, 
        ):
        """ Syncs the terragrunt config files from one stage to another (and possibly to a different domain) """
    
        if target_domain and not source_domain:
            raise Exception("Providing a target domain while omitting the source domain is not supported!")
        if source_domain and not target_domain:
            raise Exception("Providing a source domain while omitting the target domain is not supported!")

        if target_domain and not target_stage:
            self.printer.verbose(f"No target stage given, assume the same as source stage")
            target_stage=source_stage

        if not source_domain and not target_domain and not target_stage:
            raise Exception("When not providing domains, you need to provide a target stage!")

        # do we have a working dir?
        working_dir = working_dir if working_dir else os.getcwd()
        # the domains will be ignored when omitted as input
        source_path = os.path.join(working_dir, source_domain, source_stage, module, '')
        target_path = os.path.join(working_dir, target_domain, target_stage, module, '')

        self._run_sync(
            source_path=source_path,
            target_path=target_path,
            source_domain=source_domain,
            source_stage=source_stage,
            target_stage=target_stage,
            include_lock_file=include_lock_file,
            auto_approve=auto_approve,
            dry_run=dry_run,
            clean_up=clean_up,
        )

    def sync_dir(
        self, source_directory, target_directory,
        auto_approve, dry_run, clean_up, include_lock_file, working_dir, 
        ):
        """ Syncs the terragrunt config files from one directory to anothery """
    
        # do we have a working dir?
        working_dir = working_dir if working_dir else os.getcwd()
        # the domains will be ignored when omitted as input
        source_path = os.path.join(working_dir, source_directory, '')
        target_path = os.path.join(working_dir, target_directory, '')

        self._run_sync(
            source_path=source_path,
            target_path=target_path,
            include_lock_file=include_lock_file,
            auto_approve=auto_approve,
            dry_run=dry_run,
            clean_up=clean_up,
        )

    def deploy(
        self, manifest_file, version_tag, target_stage,
        include_global_config_files, auto_approve, dry_run, working_dir, 
        ):
        """ Deploys the terragrunt config files from a git repository """

        DEFAULT_VERSION='latest'

        try:
            temp_dir = os.path.join(tempfile.mkdtemp(prefix='tgwrap-'), "tg-source")

            # do we have a working dir? 
            working_dir = working_dir if working_dir else os.getcwd()

            manifest = self.load_yaml_file(os.path.join(working_dir, manifest_file))

            source_dir = os.path.join(temp_dir, manifest['base_path'])
            target_dir = os.path.join(working_dir, target_stage)

            try:
                os.mkdir(target_dir)
            except FileExistsError:
                pass

            # clone the repo
            cmd = f"git clone {manifest['git_repository']} {temp_dir}"
            rc = subprocess.run(
                shlex.split(cmd),
                check=True,
                stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
                )
            self.printer.verbose(rc)

            # now check out the specific version if we don't want latest
            if version_tag.lower() != DEFAULT_VERSION:
                cmd = f"git checkout -b source {version_tag}"
                rc = subprocess.run(
                    shlex.split(cmd),
                    cwd=temp_dir,
                    check=True,
                    stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                    stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
                    )
                self.printer.verbose(rc)

            # collect all the base paths of the substacks as you don't want
            # to include them in regular syncs
            substacks = []
            for ss, substack in manifest.get('sub_stacks', {}).items():
                # get the base directory of the sub stack so that we can ignore it when deploying the regular modules
                substacks.append(substack['source'].split(os.path.sep)[0])

            deploy_actions = {}
            for key, value in manifest['deploy'].items():
                if target_stage not in value['applies_to_stages']:
                    self.printer.verbose(f'Target stage {target_stage} not applicable for action {key}.')
                else:
                    source_stage = value['source_stage']
                    self.printer.verbose(f'Found deployment step {key} using source stage {source_stage}')

                    source_path = os.path.join(source_dir, source_stage)
                    source_modules = {
                        entry:{} for entry in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, entry))
                    }
                    self.printer.verbose(f'Found modules: {source_modules}')

                    include_modules = value['include_modules'] if len(value.get('include_modules', {})) > 0 else source_modules
                    self.printer.verbose(f'Include modules: {include_modules}')

                    # optionally, the moduels can be placed in another dir than the current
                    base_dir = value.get('base_dir', '')

                    for module, module_details in include_modules.items():
                        source_module = module_details.get('source', module)
                        target_module = module_details.get('target', module)
                        if source_module in value.get('exclude_modules', []) or source_module in substacks:
                            self.printer.verbose(f'Exclude module {source_module}')
                        else:
                            key = f'base -> {os.path.join(base_dir, module)}' if base_dir else module
                            deploy_actions[key] = {
                                "source": os.path.join(source_path, source_module, ''),
                                "target": os.path.join(target_dir, base_dir, target_module, ''),
                            }

                    for ss, substack in manifest.get('sub_stacks', {}).items():
                        self.printer.verbose(f'Found substack : {ss}')

                        source_path = os.path.join(
                            source_dir, source_stage, substack['source'], ''
                            )
                        target_path = os.path.join(
                            target_dir, substack['target'], ''
                            )

                        exclude_modules =substack.get('exclude_modules', [])
                        if os.path.exists(source_path):
                            deploy_actions[f'substack -> {substack["target"]}'] = {
                                "source": source_path,
                                "target": target_path,
                                "excludes": exclude_modules,
                            }
                        else:
                            self.printer.warning(f'Source path of substack does not exist: {source_path}')

            if include_global_config_files:
                for gc, global_config in manifest.get('global_config_files', {}).items():
                    self.printer.verbose(f'Found global config : {gc}')

                    source_path = os.path.join(
                        source_dir, global_config['source']
                        )
                    target = global_config.get('target', global_config['source'])
                    target_path = os.path.join(
                        working_dir, target,
                        )

                    if os.path.exists(source_path):
                        deploy_actions[f'global configs -> {target}'] = {
                            "source": source_path,
                            "target": target_path,
                        }
                    else:
                        self.printer.warning(f'Source path of global configs does not exist: {source_path}')
            else:
                self.printer.verbose(f'Skipping global configs')

            self.printer.header('Modules to deploy:')
            self.printer.normal(f'-> git repository: {manifest["git_repository"]}')
            self.printer.normal(f'-> version tag: {version_tag}')
            self.printer.normal('Modules:')
            for key, value in deploy_actions.items():
                self.printer.normal(f'--> {key}')

            if not auto_approve:
                response = input("\nDo you want to continue? (y/n) ")
                if response.lower() != "y":
                    sys.exit(1)

            for key, value in deploy_actions.items():
                self._run_sync(
                    source_path=value['source'],
                    target_path=value['target'],
                    excludes=value.get('excludes', []),
                    include_lock_file=True,
                    auto_approve=True,
                    dry_run=dry_run,
                    clean_up=False,
                )

            if not dry_run:
                with open(os.path.join(target_dir, 'version.hcl'), 'w') as f:
                    f.write(f"""
locals {{
    version_tag="{version_tag}"
}}
""")
        except KeyError as e:
            self.printer.error(f'Error interpreting the manifest file. Please ensure it uses the proper format. Could not find element: {e}')
            sys.exit(1)
        except Exception as e:
            self.printer.error(f'Unexpected error: {e}')
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def show_graph(self, backwards, exclude_external_dependencies, working_dir, include_dir, exclude_dir, terragrunt_args):
        """ Shows the dependencies of a project """

        self.printer.verbose(f"Attempting to show dependencies")
        if terragrunt_args:
            self.printer.verbose(f"- with additional parameters: {' '.join(terragrunt_args)}")

        # self.printer.verbose(f"Include dirs: {'; '.join(include_dir)}")
        # self.printer.verbose(f"Exclude dirs: {'; '.join(exclude_dir)}")

        "Runs the desired command in the directories as defined in the directed graph"
        graph = self._get_di_graph(backwards=backwards, working_dir=working_dir)

        # first go through the groups and clean up where needed
        groups = self._prepare_groups(
            graph=graph,
            exclude_external_dependencies=exclude_external_dependencies,
            working_dir=working_dir,
            include_dir=include_dir,
            exclude_dir=exclude_dir,
            )

        self.printer.header("The following groups will be processed:")
        for idx, group in enumerate(groups):
            self.printer.normal(f"\nGroup {idx+1}:")
            for directory in group:
                self.printer.normal(f"- {directory}")

    def clean(self, working_dir):
        """ Clean the temporary files of a terragrunt/terraform project """

        cmd = 'find . -name ".terragrunt-cache" -type d -exec rm -rf {} \; ; find . -name ".terraform" -type d -exec rm -rf {} \;'
        rc = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
            stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            cwd=working_dir if working_dir else None,
            )
        self.printer.verbose(rc)
        self.printer.normal("Cleaned the temporary files")

