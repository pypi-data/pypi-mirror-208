from color_palette_extract import color_palette_extract
import timeit
import datetime

f = open("test/instagram.png", mode="rb")
file_bytes = f.read()
start = datetime.datetime.now()
result = color_palette_extract.extract_from_bytes(file_bytes)
finish = datetime.datetime.now()
print(finish - start)
print(result)

results = timeit.timeit(
    lambda: color_palette_extract.extract_from_bytes(file_bytes), number=10
)
print(results)
