from fastapi import UploadFile

class FileTooLargeException(Exception):
	pass

async def read_file_in_chunks(file: UploadFile, chunk_size: int = 1024, max_size: int = -1):
	"""Read a file asynchronously in chunks. If max_size is provided, raise """
	total_size = 0
	while True:
		chunk = await file.read(chunk_size)
		if not chunk:
			break
		total_size += len(chunk)
		if total_size > max_size > 0:
			raise FileTooLargeException(f"File exceeded maximum size of {max_size}")
		yield chunk
