import docker
import os
import time
from compose.container import Container
from compose.config.config import ConfigDetails
from compose.config.config import ConfigFile
from compose.config.config import load
from compose.project import Project
from compose.cli.docker_client import docker_client
from compose.config.environment import Environment
from compose.container import Container


def build_image(image_name, dockerfile_dir):
    print("Building image %s from %s" % (image_name, dockerfile_dir))
    client = docker.from_env(assert_hostname=False)
    output = client.build(dockerfile_dir, rm=True, tag=image_name)
    response = "".join(["     %s" % (line,) for line in output])
    print(response)


def image_exists(image_name):
    client = docker.from_env(assert_hostname=False)
    tags = [t for image in client.images() for t in image['RepoTags']]
    return "%s:%s" % (image_name, "latest") in tags


def run_docker_command(**kwargs):
    client = docker.from_env(assert_hostname=False)
    container = TestContainer.create(client, **kwargs)
    container.start()
    container.wait()
    logs = container.logs()
    container.shutdown()
    return logs


def path_exists_in_image(image, path):
    print image
    print path
    cmd = "bash -c '[ ! -e %s ] || echo success' " % (path,)
    print cmd
    output = run_docker_command(image=image, command=cmd)
    print(output)
    return "success" in output


class TestContainer(Container):

    def state(self):
        return self.inspect_container["State"]

    def status(self):
        return self.state()["Status"]

    def shutdown(self):
        self.stop()
        self.remove()

    def execute(self, command):
        eid = self.create_exec(command)
        return self.start_exec(eid)


class TestCluster():

    def __init__(self, name, working_dir, config_file):
        config_file_path = os.path.join(working_dir, config_file)
        cfg_file = ConfigFile.from_filename(config_file_path)
        c = ConfigDetails(working_dir, [cfg_file],)
        cd = load(c)
        self.client = docker_client(Environment())
        self.project = Project.from_config(name, cd, self.client)

    def start(self):
        self.project.up()

    def is_running(self):
        state = [container.is_running for container in self.project.containers()]
        return all(state) and len(state) > 0

    def shutdown(self):
        self.project.stop()
        self.project.remove_stopped()

    def get_container(self, service_name):
        print self.project.get_services()
        return self.project.get_service(service_name).get_container()

    def run_command_on_service(self, service_name, command):
        return self.run_command(command, self.get_container(service_name))

    def run_command(self, command, container):
        print command
        eid = container.create_exec(command)
        return container.start_exec(eid)

    def run_command_on_all(self, command):
        results = {}
        for container in self.project.containers():
            results[container.name_without_project] = self.run_command(command, container)

        return results
