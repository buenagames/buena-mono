name: "Buena Mono"
designer: "Buena"
license: "OFL"
category: "MONOSPACE"
date_added: "2026-02-05"

fonts {
  name: "Buena Mono"
  style: "normal"
  weight: 400
  filename: "BuenaMono[slnt,wght].ttf"
  post_script_name: "BuenaMono-Regular"
  full_name: "Buena Mono Regular"
  copyright: "Copyright 2026 The Buena Mono Project Authors (https://github.com/buenagames/buena-mono)."
}

fonts {
  name: "Buena Mono"
  style: "italic"
  weight: 400
  filename: "BuenaMono[slnt,wght].ttf"
  post_script_name: "BuenaMono-Italic"
  full_name: "Buena Mono Italic"
  copyright: "Copyright 2026 The Buena Mono Project Authors (https://github.com/buenagames/buena-mono)."
}

subsets: "cyrillic"
subsets: "cyrillic-ext"
subsets: "greek"
subsets: "greek-ext"
subsets: "latin"
subsets: "latin-ext"
subsets: "math"
subsets: "menu"
subsets: "symbols"
subsets: "symbols2"
subsets: "vietnamese"

axes {
  tag: "slnt"
  min_value: -10.0
  max_value: 0.0
}

axes {
  tag: "wght"
  min_value: 100.0
  max_value: 800.0
}

source {
  repository_url: "https://github.com/buenagames/buena-mono"
  branch: "main"
  files {
    source_file: "out/fonts/BuenaMono-VF.ttf"
    dest_file: "BuenaMono[slnt,wght].ttf"
  }
  files {
    source_file: "OFL.txt"
    dest_file: "OFL.txt"
  }
}

stroke: "SANS_SERIF"
classifications: "MONOSPACE"
primary_script: "Latn"
minisite_url: "https://buena-mono.buenalabs.io"
