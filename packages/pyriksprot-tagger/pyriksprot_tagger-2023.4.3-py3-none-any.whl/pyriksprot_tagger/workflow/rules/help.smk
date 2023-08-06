# type: ignore

rule help_main:
    input:
        "Snakefile",
    shell:
        "sed -n 's/^##//p' {input}"
