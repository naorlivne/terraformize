resource "null_resource" "test" {
  count   = 1
}


output "test" {
  # the variable below should be missing so it will break for testing non runnable terraform files behvior in the system
  value = var.test
}
