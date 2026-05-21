# ==============================
# Windows to Linux Script
# ==============================
# REQUIREMENTS
# ------------
# - OpenSSH client installed on Windows
# - SSH access to Linux server
# - SCP available on the system
# ==============================

# -------- USER VARIABLES --------
$SourcePath = "C:\projects"
$LinuxUser  = "manish"
$LinuxIP    = "192.168.137.134"
$DestPath   = "/home/manish/Transfer"
# --------------------------------

# Build remote target properly FIRST
$RemoteHost   = "${LinuxUser}@${LinuxIP}"
$RemoteTarget = "${RemoteHost}:${DestPath}"

# Create destination directory on Linux
ssh $RemoteHost "mkdir -p ${DestPath}"

# Create output file with timestamp for logging
$timeStamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outputFile = "output_$timeStamp.txt"
$cutoffDate = (Get-Date).AddDays(-7)


Write-Host "-----------------------------------------------------"
Write-Host "STARTING WINDOWS → LINUX FILE TRANSFER"
Write-Host "Source      : $SourcePath"
Write-Host "Destination : $RemoteTarget"
Write-Host "Log File    : $outputFile"
Write-Host "-----------------------------------------------------`n"

Add-Content -Path $outputFile -Value "Transfer started at: $(Get-Date)"
Add-Content -Path $outputFile -Value "Source Path: $SourcePath"
Add-Content -Path $outputFile -Value "Destination: $RemoteTarget"
Add-Content -Path $outputFile -Value "-----------------------------------------------------"

# Function to process a folder and its subfolders
function Process-Folder {
    param (
        [string]$folderName
    )

    # Check if the source folder exists
    $fullSourcePath = Join-Path -Path $SourcePath -ChildPath $folderName
    if (-not (Test-Path $fullSourcePath)) {
        $msg = "WARNING: Source folder does not exist: $fullSourcePath - Skipping."
        Write-Warning $msg
        Add-Content -Path $outputFile -Value $msg
        return
    }

    Write-Host "Processing folder: $folderName" -ForegroundColor Cyan
    Add-Content -Path $outputFile -Value "Processing folder: $folderName"

    # Recursively copying all files in the folder in similar structure to Linux
    foreach ($file in Get-ChildItem $fullSourcePath -Recurse -File) {
        $fullFilePath = $file.FullName

        $relativePath = $fullFilePath.Substring($SourcePath.Length)
        $relativePath = $relativePath -replace "\\","/"

        $remoteFile = "${DestPath}${relativePath}"
        $remoteDir  = $remoteFile.Substring(0, $remoteFile.LastIndexOf("/"))

        ssh $RemoteHost "mkdir -p $remoteDir"

        try {
            Write-Host "Copying file: $fullFilePath" -ForegroundColor Green
            Add-Content -Path $outputFile -Value "Copying file: $fullFilePath"

            # Execute the scp file transfer
            scp "$fullFilePath" "${RemoteHost}:$remoteFile"

            if ($LASTEXITCODE -eq 0) {
                $msg = "SUCCESS: $relativePath"
                Write-Host $msg -ForegroundColor Yellow
                Add-Content $outputFile $msg
            }
            else {
                $msg = "FAILED: $relativePath"
                Write-Warning $msg
                Add-Content $outputFile $msg
            }
        } catch {
            $msg = "ERROR copying file: $fullFilePath - $_"
            Write-Warning $msg -ForegroundColor Red
            Add-Content -Path $outputFile -Value $msg
        }
    }

    # Deletes Windows files older than 7 days AFTER verification
    $deleteCount = 0
    $sourceFiles = Get-ChildItem $fullSourcePath -Recurse -File | Where-Object { $_.LastWriteTime -lt $cutoffDate }

    foreach ($file in $sourceFiles) {
        $fullFilePath = $file.FullName
        $relativePath = $fullFilePath.Substring($SourcePath.Length)
        $relativePath = $relativePath -replace "\\","/"

        $destFilePath = "$DestPath/$relativePath"

        # Check if file exists on Linux and retrieve its size
        $checkCmd = "test -f '$destFilePath' && stat -c%s '$destFilePath' || echo NOT_FOUND"
        $remoteSize = (ssh $RemoteHost $checkCmd).Trim()

        if ($remoteSize -ne "NOT_FOUND") {

            # Compare Linux file size with Windows file size
            if ([int64]$remoteSize -eq $file.Length) {
                $msg = "VERIFIED on Linux → deleting file from windows: $fullFilePath"
                Write-Host $msg -ForegroundColor Blue
                Add-Content $outputFile $msg
                try {
                    Remove-Item $fullFilePath -Force -ErrorAction Stop
                    $deleteCount++
                }
                catch {
                    $warnmsg = "Delete failed: $fullFilePath : $_"
                    Write-Warning $warnmsg -ForegroundColor Red
                    Add-Content $outputFile $warnmsg
                }
            }
            else {
                $warnmsg = "Size mismatch on Linux, skipping delete: $relativePath"
                Write-Warning $warnmsg -ForegroundColor Yellow
                Add-Content $outputFile $warnmsg
            }
        }
        else {
            $msg = "File not present on Linux → skip delete: $relativePath"
            Write-Host $msg -ForegroundColor Gray
            Add-Content $outputFile $msg
        }
    }
    Add-Content $outputFile "Total files deleted: $deleteCount"
}

Process-Folder "."

Write-Host "`n-----------------------------------------------------"

if ($LASTEXITCODE -eq 0) {
    Write-Host "TRANSFER PROCESS COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Add-Content $outputFile "Transfer completed successfully."
}
else {
    Write-Host "TRANSFER PROCESS COMPLETED WITH ERRORS" -ForegroundColor Red
    Add-Content $outputFile "Transfer finished with errors."
}

Write-Host "Log file saved at: $outputFile"
Write-Host "-----------------------------------------------------"