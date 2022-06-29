
install:
	pip install .
	pip install -r requirements.txt

# GENERATE PYTHON FILES FROM PROTOS
ONDEWO_S2T_API_DIR=ondewo-s2t-api
ONDEWO_PROTOS_DIR=${ONDEWO_S2T_API_DIR}/ondewo/

build_compiler:
	make -C ondewo-proto-compiler/python build


generate_ondewo_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${ONDEWO_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'

push_to_pypi: build_package upload_package clear_package_data
	echo 'pushed to pypi :)'

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
