
install:
	pip install .
	pip install -r requirements.txt

# GENERATE PYTHON FILES FROM PROTOS
PROTO_OUTPUT_FOLDER=ondewo
PROTO_COMPILER_IMAGE_NAME=registry-dev.ondewo.com:5000/ondewo/ondewo-python-proto-compiler
PROTO_DIR=ondewo-s2t-api/ondewo/s2t
EXTRA_PROTO_DIR=googleapis/google
TARGET_DIR=

generate_ondewo_protos:
	-mkdir ${PROTO_OUTPUT_FOLDER}
	docker run \
		--user ${shell id -u}:${shell id -g} \
		-v ${shell pwd}/${PROTO_OUTPUT_FOLDER}:/home/ondewo/ondewo-proto-compiler/output \
		-v ${shell pwd}/${PROTO_DIR}:/home/ondewo/ondewo-proto-compiler/protos/${shell basename ${PROTO_DIR}} \
		-v ${shell pwd}/${EXTRA_PROTO_DIR}:/home/ondewo/ondewo-proto-compiler/protos/${shell basename ${EXTRA_PROTO_DIR}} \
		-e INTERNAL_TARGET_PROTO_DIR=${TARGET_DIR} \
		${PROTO_COMPILER_IMAGE_NAME}


push_to_pypi: build_package upload_package clear_package_data
	echo 'pushed to pypi :)'

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
