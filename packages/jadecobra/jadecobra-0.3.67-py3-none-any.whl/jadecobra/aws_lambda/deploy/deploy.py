import argparse
from . import lambda_function
from . import lambda_layer

def main():
    parser = argparse.ArgumentParser(
        description="Update Existing Lambda Functions or Publish Layers"
    )
    parser.add_argument(
        "-f",
        "--deploy_function",
        help="Package and Deploy a Lambda Function to S3. Update the Lambda Function if it exists",
    )
    parser.add_argument(
        "-l", "--publish_layer",
        nargs="+",
        help="Package and Publish Lambda Layer(s)"
    )
    parser.add_argument("-b", "--bucket_name", required=True)
    parser.add_argument("-p", "--profile_name")

    args = parser.parse_args()

    # Add calls to respective classes
    # Implement subparsers to replace if statements
    if args.deploy_function:
        print(f"\tCreating Package for {args.deploy_function}")
        lambda_function.LambdaFunction(
            args.deploy_function,
            bucket_name=args.bucket_name,
            profile_name=args.profile_name,
        )
    if args.publish_layer:
        print(
            f'\tCreating Lambda Layer for dependencies: {", ".join(args.publish_layer)}'
        )
        lambda_layer.LambdaLayer(
            args.publish_layer,
            bucket_name=args.bucket_name,
            profile_name=args.profile_name,
        )


if __name__ == '__main__':
    main()