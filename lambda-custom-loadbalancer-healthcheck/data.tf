data "aws_lb" "this" {
  arn = var.alb_arn
}

data "aws_lb_target_group" "this" {
  arn = var.target_group_arn
}