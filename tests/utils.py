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
import json


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


def pull_image(image_name):
    client = docker.from_env(assert_hostname=False)
    client.pull(image_name)


def run_docker_command(**kwargs):
    pull_image(kwargs["image"])
    client = docker.from_env(assert_hostname=False)
    container = TestContainer.create(client, **kwargs)
    container.start()
    container.wait()
    logs = container.logs()
    container.shutdown()
    return logs


def path_exists_in_image(image, path):
    print "Checking for %s in %s" % (path, image)
    cmd = "bash -c '[ ! -e %s ] || echo success' " % (path,)
    output = run_docker_command(image=image, command=cmd)
    return "success" in output


def run_command_on_host(command):
    logs = run_docker_command(
            image="busybox",
            command=command,
            host_config={'NetworkMode': 'host', 'Binds': ['/tmp:/tmp']})
    print "Running command %s: %s" % (command, logs)
    return logs


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
        self.cd = load(c)
        self.name = name

    def get_project(self):
        # Dont reuse the client to fix this bug : https://github.com/docker/compose/issues/1275
        client = docker_client(Environment())
        project = Project.from_config(self.name, self.cd, client)
        return project

    def start(self):
        self.get_project().up()

    def is_running(self):
        state = [container.is_running for container in self.get_project().containers()]
        return all(state) and len(state) > 0

    def is_service_running(self, service_name):
        return self.get_container(service_name).is_running

    def shutdown(self):
        project = self.get_project()
        project.stop()
        project.remove_stopped()

    def get_container(self, service_name):
        return self.get_project().get_service(service_name).get_container()

    def run_command_on_service(self, service_name, command):
        return self.run_command(command, self.get_container(service_name))

    def service_logs(self, service_name, stopped=False):
        if stopped:
            containers = self.get_project().containers([service_name], stopped=True)
            return containers[0].logs()
        else:
            return self.get_container(service_name).logs()

    def run_command(self, command, container):
        eid = container.create_exec(command)
        output = container.start_exec(eid)
        print "Running %s on %s : %s " % (command, container, output)
        return output

    def run_command_on_all(self, command):
        results = {}
        for container in self.get_project().containers():
            results[container.name_without_project] = self.run_command(command, container)

        return results
