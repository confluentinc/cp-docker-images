from behave import *
import docker
import os

IMAGE_DIR = os.path.join(os.getcwd(), "..")


@when(u'I build {image_name} from {basedir}')
def step_impl(context, image_name, basedir):
    client = docker.from_env(assert_hostname=False)
    output = client.build(os.path.join(IMAGE_DIR, basedir), rm=True, tag=image_name)
    response = ["     %s" % (line,) for line in output]
    print(response)
    return True


@then(u'a {image_name} image should exist')
def step_impl(context, image_name):
    client = docker.from_env(assert_hostname=False)
    tags = [t for image in client.images() for t in image['RepoTags']]
    assert("%s:latest" % (image_name,) in tags)
