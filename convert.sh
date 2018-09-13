for file in papers/*.pdf; do pdftotext "$file" "txt-$file.txt"; done
