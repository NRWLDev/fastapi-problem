def pre_mutation(context) -> None:  # noqa: ANN001
    line = context.current_source_line.strip()
    if "# nomut" in line:
        context.skip = True
