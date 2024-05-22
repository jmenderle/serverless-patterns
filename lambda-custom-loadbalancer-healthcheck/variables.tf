variable "alb_arn" {
  type        = string
  nullable    = false
  description = "ARN of the ALB"
  validation {
    condition     = can(regex("^arn:aws:[a-z0-9-]+:[a-z0-9-]+:[0-9]{12}:.*$", var.alb_arn))
    error_message = "The provided ARN '${var.alb_arn}' is not a valid AWS ARN."
  }
}

variable "target_group_arn" {
  type        = string
  nullable    = false
  description = "ARN of the Target Group"
  validation {
    condition     = can(regex("^arn:aws:[a-z0-9-]+:[a-z0-9-]+:[0-9]{12}:.*$", var.target_group_arn))
    error_message = "The provided ARN '${var.target_group_arn}' is not a valid AWS ARN."
  }
}

variable "health_check_body_value" {
  type     = string
  nullable = true
  default  = null
}