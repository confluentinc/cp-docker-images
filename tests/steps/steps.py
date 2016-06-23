from behave import *
import docker
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.environ.get("IMAGE_DIR") or os.path.join(CURRENT_DIR, "..", "..")


class TestContainer():

    def __init__(self, image_name, command=None, env=None):
        self.client = docker.from_env(assert_hostname=False)
        self.image_name = image_name
        self.command = command
        self.env = env
        self.container = self.client.create_container(image="%s:latest" % (image_name,), command=command, environment=env)

    def start(self):
        self.client.start(self.container)
        self.client.wait(self.container)

    def logs(self):
        return self.client.logs(self.container)

    def shutdown(self):
        self.client.stop(self.container)
        self.client.remove(self.container)

    def get_file(self, path):
        return self.client.copy(self.container, path)

# def run_docker_command(image, cmd=None):
#     client = docker.from_env(assert_hostname=False)
#     if cmd:
#         c = client.create_container(image="%s:latest" % (image,), command=str(cmd))
#     else:
#         c = client.create_container(image="%s:latest" % (image,))
#     client.start(c)
#     client.wait(c)
#     logs = client.logs(c)
#     client.remove_container(c)
#     print("Ran command %s on image %s." % (cmd, image))
#     print("Output :  %s " % (logs,))
#     return logs
#
#
# def start_docker_container(image, cmd=None, env=None):
#     client = docker.from_env(assert_hostname=False)
#     c = client.create_container(image="%s:latest" % (image,), command=cmd, environment=env)
#     client.start(c)
#     client.wait(c)
#     logs = client.logs(c)
#     print("Started container with command %s on image %s." % (cmd, image))
#     print("Output :  %s " % (logs,))
#     return (c, logs)
#
#
# def shutdown_container(c):
#     client = docker.from_env(assert_hostname=False)
#     client.stop(c)
#     client.remove(c)
#
# def copy_file_from_container(container, file_path):
#     client = docker.from_env(assert_hostname=False)
#     return client.copy(container, file_path)


@when(u'I build image {image_name} from {basedir}')
def step_impl(context, image_name, basedir):
    full_image_path = os.path.join(IMAGE_DIR, basedir)
    print("Building image %s from %s" % (full_image_path, basedir))
    client = docker.from_env(assert_hostname=False)
    output = client.build(full_image_path, rm=True, tag=image_name)
    response = ["     %s" % (line,) for line in output]
    print(response)
    return True


@given(u'an image {image_name} exists')
@then(u'a {image_name} image should exist')
def step_impl(context, image_name):
    client = docker.from_env(assert_hostname=False)
    tags = [t for image in client.images() for t in image['RepoTags']]
    context.image_name = image_name
    assert("%s:latest" % (image_name,) in tags)


@when(u'I run {cmd} on it')
def step_impl(context, cmd):
    image = context.image_name
    context.container = TestContainer(image, cmd)
    context.container.start()


@then(u'I should see {output}')
def step_impl(context, output):
    assert(output in context.container.logs())


@then(u'it should have path {path}')
def step_impl(context, path):
    image = context.image_name
    cmd = "bash -c '[ -e %s ] || echo fail' " % (path,)
    container = TestContainer(image, cmd)
    container.start()
    assert("fail" not in container.logs())


@then(u'it should have executable {path}')
def step_impl(context, path):
    image = context.image_name
    cmd = "bash -c '[ -x %s ] || echo fail' " % (path,)
    container = TestContainer(image, cmd)
    container.start()
    assert("fail" not in container.logs())


@given(u'the environment variables are')
def step_impl(context):
    context.environment = {}
    for row in context.table:
        context.environment[row['name']] = row['value']


@when(u'I start {image_name}')
def step_impl(context, image_name):
    env = context.image_name
    container, logs = start_docker_container(image_name, env=env)
    # Add this to context for the shutdown command
    context.container = container
    context.image_name = image_name


@then(u'it should have {config_file} with {fixture_name} properties')
def step_impl(context, config_file, fixture_name):
    file_contents = copy_file_from_container(context.container, config_file)
    import filecmp
    fixture_path = os.path.join(CURRENT_DIR, "..", "fixtures", image_name, fixture_name)
    with open(fixture_path, 'r') as fixture_file:
        fixture_contents = fixture_file.read()
    assert(file_contents == fixture_contents)


@then(u'shutdown cleanly')
def step_impl(context):
    shutdown_container(context.container)
