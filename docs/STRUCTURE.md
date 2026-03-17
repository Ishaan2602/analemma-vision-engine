# Directory Structure

```
analemma_project/
├── README.md
├── requirements.txt
├── analemma_cli.py              # CLI interface
├── create_input.py              # Scaffolds new input image directories
│
├── analemma/                    # Core engine (5 modules)
│   ├── calculator.py            # Solar declination + EoT (approximate & HP)
│   ├── sky_mapper.py            # Celestial -> horizon coords, IANA timezone
│   ├── plotter.py               # Matplotlib visualizations (6 plot types)
│   ├── image_anchor.py          # CV sun detection + overlay rendering
│   └── metadata_parser.py       # KEY=VALUE parser, flexible coordinate formats
│
├── input_images/                # One folder per image, each with metadata.txt
│   ├── hongkong/
│   ├── nigeria/
│   ├── sharjah_sands/
│   └── ...
│
├── output/                      # Generated overlays, sky charts, composites
│   ├── hongkong_output/
│   └── ...
│
├── demo_scripts/
│   └── process_image.py         # Main processing script for any input image
│
├── examples/                    # Standalone usage examples
│   ├── basic_plot.py
│   ├── uiuc_noon.py
│   ├── image_overlay.py
│   └── mode_comparison.py
│
├── tests/
│   └── test_calculator.py
│
├── docs/                        # All documentation
│   ├── TECHNICAL_DESCRIPTION.md
│   ├── THEORY_AND_LIMITATIONS.md
│   ├── USAGE_GUIDE.md
│   ├── METADATA_REFERENCE.md
│   ├── PROJECT_BRIEF.md
│   ├── PROJECT_LOG.md
│   ├── IMPLEMENTATION_NOTES.md
│   ├── CV_debugging.md
│   └── STRUCTURE.md
│
├── analemma_resources/          # Reference PDFs and images
├── analysis.ipynb               # Interactive testing notebook
└── .github/copilot-instructions.md
```

## Getting started

1. `pip install -r requirements.txt`
2. `python demo_scripts/process_image.py hongkong` to process an image
3. Add your own images to `input_images/yourname/` with a `metadata.txt`
4. See `examples/` for Python API usage, or `python analemma_cli.py --help` for CLI
