all_full: build_full run_full

build_full:
	docker build -f Dockerfile.full -t austindarrow/dashboard:1.0 .

run_full:
	docker run --rm -p 8050:8050 austindarrow/dashboard:1.0

all_lite: build_lite run_lite

build_lite:
	docker build -f Dockerfile.lite -t austindarrow/dashboard-lite:1.0 .

run_lite:
	docker run --rm -p 8051:8051 austindarrow/dashboard-lite:1.0