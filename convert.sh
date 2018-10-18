for file in papers/*.pdf; do echo $file; pdftotext "$file" "txt-$file.txt"; done
