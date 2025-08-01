CONFIG ?= Debug
ARCH ?= x64
PLATFORM ?= windows
COMPILER ?= any

all: build

build:
	python3 -m scripts.compile --config=$(CONFIG) --arch=$(ARCH) --platform=$(PLATFORM) --compiler=$(COMPILER)