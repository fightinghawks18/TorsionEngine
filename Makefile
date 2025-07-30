CONFIG ?= Debug
ARCH ?= x64
PLATFORM ?= windows

all: build

build:
	python3 -m scripts.compile --config=$(CONFIG) --arch=$(ARCH) --platform=$(PLATFORM)