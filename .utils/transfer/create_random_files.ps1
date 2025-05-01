# Create 20 empty files named document_1.txt through document_20.txt
for ($i = 1; $i -le 20; $i++) {
    $fileName = "document_$i.txt"
    New-Item -Path $fileName -ItemType File -Force | Out-Null
    Write-Host "Created file: $fileName"
}

Write-Host "Created 20 empty text files successfully."