# Makefile for building and pushing the llama.cpp CPU SageMaker image to ECR
SHELL := /bin/bash

# Configuration (override via env or CLI)
REPO_NAME ?= fdtn-llama-cpp-cpu
REGION ?= $(shell aws configure get region 2>/dev/null || echo us-west-2)
VERSION ?= latest
PLATFORM ?= linux/amd64

# Derived values
ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
REGISTRY := $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
REPO_URI := $(REGISTRY)/$(REPO_NAME)

.PHONY: build publish

build:
	@docker build \
		-f Dockerfile \
		-t "$(REPO_NAME):latest" \
		-t "$(REPO_URI):$(VERSION)" \
		-t "$(REPO_URI):latest" \
		--platform "$(PLATFORM)" \
		.
	@echo "Built: $(REPO_URI):latest"
	@echo "Built: $(REPO_URI):$(VERSION)"

publish:
	@aws ecr describe-repositories --region "$(REGION)" --repository-names "$(REPO_NAME)" >/dev/null 2>&1 || \
	  aws ecr create-repository --region "$(REGION)" --repository-name "$(REPO_NAME)" >/dev/null
	@aws ecr get-login-password --region "$(REGION)" | docker login --username AWS --password-stdin "$(REGISTRY)"
	@docker push "$(REPO_URI):latest"
	@docker push "$(REPO_URI):$(VERSION)"
	@echo "Published: $(REPO_URI):latest"
	@echo "Published: $(REPO_URI):$(VERSION)"
