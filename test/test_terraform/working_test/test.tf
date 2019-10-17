resource "null_resource" "test" {
  count   = 1
}

variable "test" {
  default = "not_set"
}

output "test" {
  value = var.test
}
