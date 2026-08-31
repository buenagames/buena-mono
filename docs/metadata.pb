name: "Buena Mono"
designer: "Buena"
license: "OFL"
category: "MONOSPACE"
date_added: "2026-02-05"

fonts {
  name: "Buena Mono"
  style: "normal"
  weight: 400
  filename: "BuenaMono[wght].ttf"
  post_script_name: "BuenaMono-Regular"
  full_name: "Buena Mono Regular"
  copyright: "Copyright 2026 The Buena Mono Project Authors (https://github.com/buenagames/buena-mono). Portions copyright 2024 The Fragment-Mono Project Authors; 2017 IBM Corp. with Reserved Font Name \"Plex\"; 2022 The Noto Project Authors; 2019-Present Microsoft Corporation with Reserved Font Name Cascadia Code; 2020 The JetBrains Mono Project Authors; 2012 Steinberg Media Technologies GmbH (Bravura). Full notices in OFL.txt."
}

fonts {
  name: "Buena Mono"
  style: "italic"
  weight: 400
  filename: "BuenaMono-Italic[wght].ttf"
  post_script_name: "BuenaMono-Italic"
  full_name: "Buena Mono Italic"
  copyright: "Copyright 2026 The Buena Mono Project Authors (https://github.com/buenagames/buena-mono). Portions copyright 2024 The Fragment-Mono Project Authors; 2017 IBM Corp. with Reserved Font Name \"Plex\"; 2022 The Noto Project Authors; 2019-Present Microsoft Corporation with Reserved Font Name Cascadia Code; 2020 The JetBrains Mono Project Authors; 2012 Steinberg Media Technologies GmbH (Bravura). Full notices in OFL.txt."
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
  tag: "wght"
  min_value: 100.0
  max_value: 800.0
}

source {
  repository_url: "https://github.com/buenagames/buena-mono"
  branch: "main"
  files {
    source_file: "out/fonts/BuenaMono[wght].ttf"
    dest_file: "BuenaMono[wght].ttf"
  }
  files {
    source_file: "out/fonts/BuenaMono-Italic[wght].ttf"
    dest_file: "BuenaMono-Italic[wght].ttf"
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
