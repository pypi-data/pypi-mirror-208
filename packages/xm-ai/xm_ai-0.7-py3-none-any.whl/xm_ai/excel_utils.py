def get_first_column_values(_worksheet):
    entries = []
    for row in _worksheet.iter_rows(min_row=1, max_row=_worksheet.max_row, min_col=1, max_col=1):
        for cell in row:
            entries.append(cell.value)
    return entries