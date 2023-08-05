def get_arn(name: str=None, region:str=None, account:str=None) -> str:
    "return arn of Lambda Function"
    return f"arn:aws:lambda:{region}:{account}:function:{name}"