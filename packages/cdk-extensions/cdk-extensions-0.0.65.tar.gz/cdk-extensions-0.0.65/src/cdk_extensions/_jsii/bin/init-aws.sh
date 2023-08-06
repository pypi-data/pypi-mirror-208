#!/usr/bin/env python

import jsii
import sys

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-extensions", "0.0.65", "cdk_extensions", "cdk-extensions@0.0.65.jsii.tgz"
)

exit_code = __jsii_assembly__.invokeBinScript(
    "cdk-extensions", "init-aws.sh", sys.argv[1:]
)
exit(exit_code)
