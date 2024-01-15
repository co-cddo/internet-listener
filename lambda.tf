locals {
  lambda_name = "web-internet-listener"
  iam_role    = "lambda-role-internet-listener"
  iam_policy  = "lambda-policy-internet-listener"
}

resource "aws_iam_role" "lambda_role" {
  name               = local.iam_role
  assume_role_policy = data.aws_iam_policy_document.arpd.json
}

resource "aws_cloudwatch_log_group" "lambda_lg" {
  name              = "/aws/lambda/${local.lambda_name}"
  retention_in_days = 365
}

resource "aws_iam_policy" "lambda_policy" {
  name        = local.iam_policy
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:logs:eu-west-2:*:/aws/lambda/${local.lambda_name}",
          "arn:aws:logs:eu-west-2:*:/aws/lambda/${local.lambda_name}:*"
        ]
      },
      {
        Action   = "s3:PutObject"
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${var.logging_bucket_name}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_pa" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

data "aws_iam_policy_document" "arpd" {
  statement {
    sid    = "AllowAwsToAssumeRole"
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_pa_vpc" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py"
  output_path = "target.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = "target.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  function_name = local.lambda_name
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"

  memory_size = 384
  timeout     = 30

  environment {
    variables = {
      S3_BUCKETNAME           = var.logging_bucket_name
      S3_PREFIX               = var.s3_prefix
      CLOUDFRONT_SECRET       = var.cloudfront_secret
      ALLOWED_CSP_SOURCES     = "gov.uk"
      ENABLE_GENERIC_REQUESTS = "true"
    }
  }

  vpc_config {
    ipv6_allowed_for_dual_stack = false
    security_group_ids = [
      "sg-0e7b2d6aa61253a30",
    ]
    subnet_ids = [
      "subnet-0a6eb6c61656fd2f2",
      "subnet-0c7440d51cbd7e14e",
    ]
  }
}

resource "aws_lambda_function_url" "lambda_latest" {
  function_name      = aws_lambda_function.lambda.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    max_age           = 0
  }
}
