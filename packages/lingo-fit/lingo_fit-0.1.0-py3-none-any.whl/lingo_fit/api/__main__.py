import argparse
import os

import uvicorn

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Thompson Sampling API")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host IP address"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--priors", type=str, help="where priors are located")
    parser.add_argument(
        "--bucket", type=str, help="S3 bucket name for the current service"
    )
    parser.add_argument("--region", type=str, help="AWS region")
    args = parser.parse_args()
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s - %(levelname)s - %(message)s"

    os.environ["S3_BUCKET"] = args.bucket
    os.environ["REGION"] = args.region
    os.environ["ARMS_PRIOR_PATH"] = args.priors

    from .recommendation_api import create_app

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port, log_config=log_config)
