from color_palette_extract import color_palette_extract

f = open("test/instagram.svg", mode="rb")
file_bytes = f.read()
result = color_palette_extract.extract_from_bytes(file_bytes)
print(result)


for res in result:
    print(color_palette_extract.get_hex_from_rgb(res[0], res[1], res[2]))
