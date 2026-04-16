# api-verification-environment/terraform/variables.tf

variable "enable_ssh" {
  type    = bool
  default = false # 基本は閉じさせておく
}
