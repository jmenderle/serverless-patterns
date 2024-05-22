data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "src/lambda.py"
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "this" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "lambda_function_payload.zip"
  function_name = "lambda_function_name"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"

  environment {
    variables = {
      alb_arn                 = var.alb_arn
      target_group_arn        = var.target_group_arn
      health_check_path       = data.aws_lb_target_group.this.health_check[0].path
      health_check_port       = data.aws_lb_target_group.this.health_check[0].port
      health_check_body_value = var.health_check_body_value
      health_check_protocol   = data.aws_lb_target_group.this.health_check[0].protocol
    }
  }
}