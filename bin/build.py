#!/usr/bin/env python3

from subprocess import Popen, call, check_call

import os
from enum import auto, Enum

print("TODO: review this list of vars for appropriateness")
print("todo: added for debugging. to be removed once integration is complete")
print("------------- ENV variables --------------------")

class EnvVars(Enum):
     COMPONENTS = auto()
     ALLOW_UNSIGNED = auto()
     CONFLUENT_PACKAGES_REPO = auto()
     KAFKA_VERSION = auto()
     CONFLUENT_MVN_LABEL = auto()
     CONFLUENT_DEB_LABEL = auto()
     CONFLUENT_DEB_VERSION = auto()
     CONFLUENT_RPM_LABEL = auto()
     CONFLUENT_MAJOR_VERSION = auto()
     CONFLUENT_MINOR_VERSION = auto()
     CONFLUENT_PATCH_VERSION = auto()
     CONFLUENT_VERSION = auto()
     VERSION = auto()
     COMMIT_ID = auto()
     BUILD_NUMBER = auto()
     REPOSITORY = auto()
     RELEASE_QUALITY = auto()
     REDHAT_USERNAME = auto()
     REDHAT_PASSWORD = auto()

class DockerArgs(Enum):
    KAFKA_VERSION = auto()
    CONFLUENT_PLATFORM_LABEL = auto()
    CONFLUENT_MAJOR_VERSION = auto()
    CONFLUENT_MINOR_VERSION = auto()
    CONFLUENT_PATCH_VERSION = auto()
    COMMIT_ID = auto()
    BUILD_NUMBER = auto()
    REDHAT_USERNAME = auto()
    REDHAT_PASSWORD = auto()


class DockerTypes(Enum):
    REDHAT = auto()
    DEBIAN = auto()

    def lcname(self) -> str:
        return self.name.lower()

#####
env_var_strs = [e.name for e in EnvVars.__members__.values()]
for env in env_var_strs:
    print(f"{env} = {os.getenv(env)}")
#####

components = os.getenv(EnvVars.COMPONENTS.name, "").split(" ")
repository = os.getenv(EnvVars.REPOSITORY.name, '368821881613.dkr.ecr.us-west-2.amazonaws.com')
confluent_version = os.getenv(EnvVars.CONFLUENT_VERSION.name)
build_number = os.getenv(EnvVars.BUILD_NUMBER.name)
commit_id = os.getenv(EnvVars.COMMIT_ID.name)
        

per_component_build_args = {
    'base': ["ALLOW_UNSIGNED", "CONFLUENT_PACKAGES_REPO", "CONFLUENT_MVN_LABEL"],
}

dockerfile_root = 'debian' # TODO for most repos this will be same as checkout root

for component in components:
    print(f"\n\nBuilding {component} \n==========================================\n")

    # the docker args for a component consist of  general docker args +
    # component-specific ones
    component_args = [da.name for da in DockerArgs.__members__.values()] + per_component_build_args.get(component, [])

    docker_build_args = " ".join([f"--build-arg {arg}=${{{arg}}}" for arg in component_args])

    for docker_type in [DockerTypes.DEBIAN, DockerTypes.REDHAT]:

        component_variant = ''
        docker_ending = ''
        confluent_platform_label = os.getenv(EnvVars.CONFLUENT_DEB_LABEL.name)

        if docker_type != DockerTypes.DEBIAN:
            component_variant = f"-{docker_type.lcname()}"
            docker_ending = f".{docker_type.lcname()}"
            confluent_platform_label = os.getenv(EnvVars.CONFLUENT_RPM_LABEL.name)

        docker_file = os.path.join(dockerfile_root, component, f"Dockerfile{docker_ending}")
        qualified_component_name = f"cp{component_variant}-{component}"

        if os.path.isfile(docker_file):
            check_call(f"sudo docker build {docker_build_args} -t {repository}/{qualified_component_name}:latest -f {docker_file} {os.path.join(dockerfile_root, component)}", shell=True)

            tags = ["latest", f"{confluent_version}", f"{confluent_version}-{build_number}", commit_id]
            for tag in tags:
                check_call(f"sudo docker tag {repository}/{qualified_component_name}:latest {repository}/{qualified_component_name}:{tag}", shell=True)
