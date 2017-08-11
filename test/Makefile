PYTHON = python3

CMD = $(PYTHON)

core_tb:
	$(CMD) core_tb.py

example_designs:
	cd ../example_designs && $(PYTHON) make.py -t simple -p minispartan6 -Ob run False build-bitstream

all: ft245_sync_tb ft245_async_tb core_tb example_designs
