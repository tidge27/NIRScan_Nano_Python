import click
import os
import logging
from github import Github
import keyring
import git
import platform
import time

import os
import asyncio
import CissUsbConnectord
import time
import hid
import logging
import platform
import threading

from start_print import start_spectrometer_log, start_ciss_log

from scan import Spectrometer, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
from spectrum_library import scan_interpret



# import pygit2


class fileStructure():
    def __init__(self, root_folder_name, create_repo=False):
        self.root_folder_name = root_folder_name
        self.measurements_folder_name = "Measurements"

        # Create the root directory
        if os.path.isdir(root_folder_name):
            if not click.confirm("Directory `{}` already exists.  Do you wish to continue with this directory".format(
                    root_folder_name), abort=True):
                logging.error(
                    "Directory `{}` already exists.  Please change the directory index for the build you wish to start".format(
                    root_folder_name))
                exit()
        else:
            os.makedirs(self.root_folder_name)
            # for sensor, directory in sensor_directories.items():
            #     structure = os.path.join(root_folder_name, measurements_folder_name, directory)
            #     os.makedirs(structure)

        self.repo = self.get_repo()
        if create_repo and not self.repo:
            try:
                self.create_repo()
            except Exception as error:
                print("Error creating git repo.  Will continue without repo creation")

    def get_repo(self):
        try:
            return git.Repo(self.root_folder_name)
        except git.InvalidGitRepositoryError as error:
            return False

    def create_repo(self):
        return
        # using personal access token
        personal_access_token = keyring.get_password('github_auth', "uname")
        if not personal_access_token:
            personal_access_token = click.prompt('Please enter a Github "Personal Access Token"')
            keyring.get_password('github_auth', "uname", personal_access_token)

        g = Github(personal_access_token)
        org = g.get_organization('physical-computation')

        # create the new repository, under the phys-comp organisation
        projectDescription = (
            """This repo is a store of the data from the print.  This repo was created by the Python tool for logging prints"""
        )
        repo = org.create_repo(self.root_folder_name, description=projectDescription)

        readme = os.path.join(self.root_folder_name, "README.md")
        open(readme, 'wb').close()

        self.repo = git.Repo.init(self.root_folder_name)
        self.repo.index.add(["README.md"])
        self.repo.index.commit("Initial Commit")
        origin = self.repo.create_remote('origin', repo.clone_url)
        self.repo.git.push("--set-upstream", "origin", "master")

    def make_dir(self, *args):
        structure = os.path.join(self.root_folder_name,*args)
        try:
            os.makedirs(structure)
        except FileExistsError as error:
            logging.warning("""File "{}" Exists already""".format(structure))
        return structure




def log_all_info():
    logging.info("Start Timestamp : {}".format(str(int(time.time() * 1000))))
    logging.info(platform.machine())
    logging.info(platform.version())
    logging.info(platform.platform())
    logging.info(platform.uname())
    logging.info(platform.system())
    logging.info(platform.processor())




@click.group()
@click.option('--directory_index')
@click.option('--create_repo/--no-create_repo', default=False)
@click.option('--logging_level', default="INFO")
@click.pass_context
def cli(ctx, directory_index, create_repo, logging_level):
    ctx.ensure_object(dict)
    root_folder_name = "sesame-" + str(directory_index).zfill(16)
    print_file = fileStructure(root_folder_name, create_repo)

    # Setup logging
    if logging_level.lower() == "debug":
        set_logging_level = logging.DEBUG
    else:
        set_logging_level = logging.INFO

    logPath = print_file.root_folder_name
    logFileName = "print_log"
    logging.basicConfig(
        level=set_logging_level,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler("{0}/{1}.log".format(logPath, logFileName)),
            logging.StreamHandler()
        ]
    )

    ctx.obj['file'] = print_file

@cli.command()
@click.option('--ciss', type=int, multiple=True)
@click.option('--spectrometer', type=int, multiple=True)
@click.option('--timeout_mins', default=0)
@click.pass_obj
def log(obj, ciss, spectrometer, timeout_mins):
    # click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    end_time = None
    if timeout_mins:
        end_time = time.time() + 60 * timeout_mins
        logging.info("Timeout set for {} mins".format(timeout_mins))
    print_file = obj['file']
    threads = []
    run_event = threading.Event()
    run_event.set()

    for count, spec_serial_no in enumerate(spectrometer):
        print("Spectrometer: ", spec_serial_no)
        folder = print_file.make_dir("Measurements", "Spectrometer-{}".format(count))
        spectrometer_log = threading.Thread(target=start_spectrometer_log, args=[run_event, folder, spec_serial_no])
        spectrometer_log.start()
        threads.append(spectrometer_log)

    for count, c in enumerate(ciss):
        print("CISS: ", c)
        folder = print_file.make_dir("Measurements", "CISS-{}".format(count))
        # Add com Port
        ciss_log = threading.Thread(target=start_ciss_log, args=[run_event, folder])
        ciss_log.start()
        threads.append(ciss_log)

    try:
        while 1:
            time.sleep(.1)
            if end_time:
                if time.time() > end_time:
                    logging.info("Timeout triggered".format(timeout_mins))
                    break
    except KeyboardInterrupt:
        pass

    logging.info("Starting to close threads.")
    run_event.clear()
    for thread in threads:
        thread.join()
    logging.info("threads successfully closed")

if __name__ == '__main__':
    cli(obj={})