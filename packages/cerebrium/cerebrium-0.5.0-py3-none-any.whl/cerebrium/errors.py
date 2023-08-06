class CerebriumRequestError(Exception):
    """
    Class to handle the error code messages from the Cerebrium API.

    Args:
        status_code (int): The status code returned from the Cerebrium API.
        endpoint (str): The endpoint that was called.
    """

    def __init__(self, status_code, endpoint, data=""):
        self.status_code = status_code
        self.endpoint = endpoint
        self.data = data
        super().__init__(self.status_code)

    def __str__(self):
        if self.status_code == 401:
            msg = f"{self.status_code}\n`{self.endpoint} API key does not exist or is incorrect. If your key is correct, please contact the Cerebrium team."
        elif self.status_code == 403:
            plan_limits = self.data.get("planLimits")
            if plan_limits:
                can_deploy_model = plan_limits.get("canDeployModel")
                number_of_plan_models = plan_limits.get("numberOfPlanModels")
                upgrade_link = plan_limits.get("upgradeLink")
                if not can_deploy_model:
                    msg = f"{self.status_code}\n`{self.endpoint}` API Call Failed. You have exceeded your model deployment limit of {number_of_plan_models}."
                    if upgrade_link:
                        msg += f" Please upgrade your plan to continue using Cerebrium at `{upgrade_link}`"
        elif str(self.status_code)[0] == "4":
            specific_message = (
                ""
                if isinstance(self.data, str)
                else " " + self.data.get("message", "") + "."
            )
            msg = f"{self.status_code}\n`{self.endpoint}` API Call Failed.{specific_message}"
        elif self.status_code == 500:
            msg = f"{self.status_code}\n`{self.endpoint}` API Call Failed. Internal Server Error: {self.data}."
        elif self.status_code == 502:
            msg = f"{self.status_code}\n`{self.endpoint}` API Call Failed. Bad Gateway."
        else:
            msg = (
                f"{self.status_code}\n`{self.endpoint}` API Call Failed.\n{self.data}."
            )
        return msg


class CerebriumDeploymentError(Exception):
    """
    Class to handle the error code messages from the Cerebrium API.

    Args:
        status_code (int): The status code returned from the Cerebrium API.
        endpoint (str): The endpoint that was called.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
