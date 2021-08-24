project {

  python = "fake.version.number"

  install = "fake install command"

}

inspect {

  source_dir = "fake-source/"

  results_dir = "fake-results/"

  output = "plain"

  suppress_levels = [
    "TYPO",
  ]

  suppress_problems = [
    "SuppressMe"
  ]

  include_files = [
    "src/include/me/*"
  ]

  exclude_files = [
    "src/exclude/me/*"
  ]

}

report {

}
