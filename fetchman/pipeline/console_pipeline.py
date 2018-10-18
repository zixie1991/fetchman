#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from fetchman.pipeline.base_pipeline import BasePipeline

class ConsolePipeline(BasePipeline):
    def on_result(self, task, result):
        print(json.dumps(result))
