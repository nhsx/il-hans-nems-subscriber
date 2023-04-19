REQFILES = ./requirements-dev.txt \
	tests/requirements.txt \
	src/nems_subscription_delete/requirements.txt \
	src/convert_hl7v2_fhir/requirements.txt \
	src/nems_subscription_create/requirements.txt \
	src/email_care_provider/requirements.txt

venv/bin/activate:
	python -m venv venv

venv/deps_installed: venv/bin/activate ${REQFILES}
	for file in ${REQFILES}; do \
	  python -m pip install -r $$file; \
	done
	touch venv/deps_installed

.PHONY: deps
deps: venv/deps_installed

.PHONY: test
test: deps
	pytest
