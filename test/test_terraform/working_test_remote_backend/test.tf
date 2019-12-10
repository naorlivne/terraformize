resource "null_resource" "test" {
  count   = 1
}

variable "test" {
  default = "not_set"
}

output "test" {
  value = var.test
}

terraform {
  backend "consul" {
    address = "consul:8500"
    scheme  = "http"
    path    = "test/test"
  }
}
