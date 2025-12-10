# TODO: add more chunking options
def chunkerize_file(file_content: list[str], chunk_size: int = 3) -> list[tuple[list[str], str]]:
    assert chunk_size > 1
    chunks = []
    idx = 0
    while idx < len(file_content):
        end = min(idx + chunk_size, len(file_content))
        chunks.append(file_content[idx:end])
        idx = end
    for i in range(0, len(chunks)):
        if len(chunks[i]) < chunk_size:
            assert i+1 == len(chunks)
            chunks.pop(i)
            break
        target = chunks[i][-1]
        chunks[i] = (chunks[i][:-1], target)
    return chunks
