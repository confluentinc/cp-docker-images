from behave import *
import docker
import os

IMAGE_DIR = os.path.join(os.getcwd(), "..")


def run_docker_command(image, cmd):
    client = docker.from_env(assert_hostname=False)
    c = client.create_container(image="%s:latest" % (image,), command=str(cmd))
    client.start(c)
    client.wait(c)
    logs = client.logs(c)
    client.remove_container(c)
    print("Ran command %s on image %s." % (cmd, image))
    print("Output :  %s " % (logs,))
    return logs


@when(u'I build {image_name} from {basedir}')
def step_impl(context, image_name, basedir):
    client = docker.from_env(assert_hostname=False)
    output = client.build(os.path.join(IMAGE_DIR, basedir), rm=True, tag=image_name)
    response = ["     %s" % (line,) for line in output]
    print(response)
    return True


@given(u'image {image_name} exists')
@then(u'a {image_name} image should exist')
def step_impl(context, image_name):
    client = docker.from_env(assert_hostname=False)
    tags = [t for image in client.images() for t in image['RepoTags']]
    assert("%s:latest" % (image_name,) in tags)


@when(u'I run {cmd} on {image}')
def step_impl(context, cmd, image):
    context.logs = run_docker_command(image, cmd)


@then(u'I should get {output}')
def step_impl(context, output):
    assert(output == context.logs)


@then(u'output should have {output}')
def step_impl(context, output):
    assert(output in context.logs)


@then(u'path {path} should exist in image {image}')
def step_impl(context, path, image):
    cmd = "bash -c '[ -e %s ] || echo fail' " % (path,)
    assert("fail" not in run_docker_command(image, cmd))
