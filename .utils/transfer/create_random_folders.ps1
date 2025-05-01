# PowerShell script to create random folders in the transfer directories
# Parameters for folder generation

# Path to the directories
$DW_Path = "C:\Users\Ali\Desktop\micro\.utils\transfer\Übergabe_aus_DW"
$OU_Path = "C:\Users\Ali\Desktop\micro\.utils\transfer\Übergabe_aus_OU"

# Random letter generation function
function Get-RandomLetters {
    param (
        [int]$Min = 3,
        [int]$Max = 5
    )
    
    $length = Get-Random -Minimum $Min -Maximum ($Max + 1)
    $letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    $result = ''
    
    for ($i = 0; $i -lt $length; $i++) {
        $index = Get-Random -Minimum 0 -Maximum $letters.Length
        $result += $letters[$index]
    }
    
    return $result
}

# Random year generation
function Get-RandomYear {
    return Get-Random -Minimum 2024 -Maximum 2031
}

# Create folders in DW directory
Write-Host "Creating folders in Übergabe_aus_DW directory..."

for ($i = 3; $i -le 22; $i++) {
    $number = $i.ToString("000")  # Format as 003, 004, etc.
    $year = Get-RandomYear
    $letters = Get-RandomLetters
    
    $folderName = "RRD$number-${year}_DW_$letters"
    $folderPath = Join-Path -Path $DW_Path -ChildPath $folderName
    
    if (!(Test-Path -Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory | Out-Null
        Write-Host "Created: $folderName"
    } else {
        Write-Host "Folder already exists: $folderName"
    }
}

# Create folders in OU directory
Write-Host "`nCreating folders in Übergabe_aus_OU directory..."

for ($i = 3; $i -le 22; $i++) {
    $number = $i.ToString("000")  # Format as 003, 004, etc.
    $year = Get-RandomYear
    $letters = Get-RandomLetters
    
    $folderName = "RRD$number-${year}_OU_$letters"
    $folderPath = Join-Path -Path $OU_Path -ChildPath $folderName
    
    if (!(Test-Path -Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory | Out-Null
        Write-Host "Created: $folderName"
    } else {
        Write-Host "Folder already exists: $folderName"
    }
}

Write-Host "`nFolder creation completed!" 