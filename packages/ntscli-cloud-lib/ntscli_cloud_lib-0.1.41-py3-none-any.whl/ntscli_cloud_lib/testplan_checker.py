#  Copyright (c) 2020 Netflix.
#  All rights reserved.

from ntscli_cloud_lib.automator import TestPlan
from ntscli_cloud_lib.log import logger


class TestPlanChecker:
    """
    Check the format of a test plan run request.

    This is a convenience class and not strictly required,
    but helps shortcut failed requests to the cloud.
    """

    @staticmethod
    def sanity_check(plan: TestPlan) -> bool:
        """Perform a basic sanity check on a plan to see if it's mostly the right shape for a request."""
        results = []

        if len(plan.testcases) < 1:
            logger.error("The test cases list is present, but empty")
            results.append(False)

        return all(results)
