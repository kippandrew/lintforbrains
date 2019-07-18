inspect {

  source_dir = "fake-source/"

  results_dir = "fake-results/"

  levels = [
    "ERROR",
    "WARNING",
  ]

  suppress = [
    "SuppressMe"
  ]

  include = [
    "src/include/me/*"
  ]

  exclude = [
    "src/exclude/me/*"
  ]

  output = "plain"

}

report {

}
