from fastapi import UploadFile

class FileTooLargeException(Exception):
	pass

async def read_file_in_chunks(file: UploadFile, chunk_size: int = 1024, max_size: int = -1) -> bytes:
	"""Read a file asynchronously in chunks. If max_size is provided, raise """
	file_data: bytes = b""
	file_size = 0
	while True:
		chunk = await file.read(chunk_size)
		if not chunk:
			break
		file_size += len(chunk)
		if file_size > max_size > 0:
			raise FileTooLargeException(f"File exceeded maximum size of {max_size}")
		file_data += chunk
	return file_data
