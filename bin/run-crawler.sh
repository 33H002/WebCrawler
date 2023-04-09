#!/bin/sh

SENTRY_RELEASE=$(git rev-parse HEAD)
export SENTRY_RELEASE

python get_ir_dataset.py