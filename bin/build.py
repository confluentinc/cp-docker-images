#!/usr/bin/env python3
from subprocess import Popen, call, check_call

print("TODO: review this list of vars for appropriateness")
print("todo: added for debugging. to be removed once integration is complete")
print("------------- ENV variables --------------------")
env_vars = [
     "COMPONENTS",
     "ALLOW_UNSIGNED",
     "CONFLUENT_PACKAGES_REPO",
     "KAFKA_VERSION",
     "CONFLUENT_MVN_LABEL",
     "CONFLUENT_DEB_LABEL",
     "CONFLUENT_DEB_VERSION",
     "CONFLUENT_RPM_LABEL",
     "CONFLUENT_MAJOR_VERSION",
     "CONFLUENT_MINOR_VERSION",
     "CONFLUENT_PATCH_VERSION",
     "CONFLUENT_VERSION",
     "VERSION",
     "COMMIT_ID",
     "BUILD_NUMBER",
     "REPOSITORY",
     "RELEASE_QUALITY",
     "REDHAT_USERNAME",
     "REDHAT_PASSWORD",
 ]

for env in env_vars:
    print(f"{env} = {os.getenv(env)}")

components = os.getenv("COMPONENTS", "")

for component in components:
    print(f"\n\nBuilding {component} \n==========================================\n")

    BUILD_ARGS = ""

    if component == "base":
        BUILD_ARGS = " ".join([f"--build-arg {arg}=${{{arg}}}" for arg in ["ALLOW_UNSIGNED", "CONFLUENT_PACKAGES_REPO", "CONFLUENT_MVN_LABEL"]])

    for docker_type in ['', 'rpm']:
        DOCKER_FILE = f"debian/{component}/Dockerfile"
        component_name=component

        if [ "${type}" = "rpm" ]; then
            component_name="rpm-${component}"
            DOCKER_FILE="${DOCKER_FILE}.rpm"
            CONFLUENT_PLATFORM_LABEL=${CONFLUENT_RPM_LABEL}
        else
            CONFLUENT_PLATFORM_LABEL=${CONFLUENT_DEB_LABEL}
        fi

        if [ -a "${DOCKER_FILE}" ]; then

docker_args = [
"KAFKA_VERSION",
"CONFLUENT_PLATFORM_LABEL",
"CONFLUENT_MAJOR_VERSION",
"CONFLUENT_MINOR_VERSION",
"CONFLUENT_PATCH_VERSION",
"COMMIT_ID",
"BUILD_NUMBER",
"REDHAT_USERNAME",
"REDHAT_PASSWORD",
]
            check_call(["sudo docker build 
KAFKA_VERSION=${{{KAFKA_VERSION}}}
CONFLUENT_PLATFORM_LABEL=${{{CONFLUENT_PLATFORM_LABEL}}}
CONFLUENT_MAJOR_VERSION=${{{CONFLUENT_MAJOR_VERSION}}}
CONFLUENT_MINOR_VERSION=${{{CONFLUENT_MINOR_VERSION}}}
CONFLUENT_PATCH_VERSION=${{{CONFLUENT_PATCH_VERSION}}}
COMMIT_ID=${{{COMMIT_ID}}}
BUILD_NUMBER=${{{BUILD_NUMBER}}}
REDHAT_USERNAME=${{{REDHAT_USERNAME}}}
REDHAT_PASSWORD=${{{REDHAT_PASSWORD}}}
${BUILD_ARGS} -t ${REPOSITORY}/cp-${COMPONENT_NAME}:latest -f ${DOCKER_FILE} debian/${component} || exit 1

            sudo docker tag ${REPOSITORY}/cp-${COMPONENT_NAME}:latest ${REPOSITORY}/cp-${COMPONENT_NAME}:latest  || exit 1
            sudo docker tag ${REPOSITORY}/cp-${COMPONENT_NAME}:latest ${REPOSITORY}/cp-${COMPONENT_NAME}:${CONFLUENT_VERSION}${CONFLUENT_MVN_LABEL} || exit 1
            sudo docker tag ${REPOSITORY}/cp-${COMPONENT_NAME}:latest ${REPOSITORY}/cp-${COMPONENT_NAME}:${VERSION} || exit 1
            sudo docker tag ${REPOSITORY}/cp-${COMPONENT_NAME}:latest ${REPOSITORY}/cp-${COMPONENT_NAME}:${COMMIT_ID} || exit 1
        fi;
    done
done
