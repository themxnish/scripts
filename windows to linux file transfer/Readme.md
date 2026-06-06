# Windows to Linux File Transfer Automation

## Overview

This PowerShell script automates file transfers from a Windows machine to a Linux server using SSH and SCP. It preserves the original folder structure, generates transfer logs, verifies successful transfers, and removes old source files only after validation.

---

## Features

* Secure file transfer using SCP with timestamp-based logging
* Automatic remote directory creation with Recursive file and folder processing 
* Preserves source directory structure
* File transfer verification using file size comparison
* Automatic cleanup of files older than 7 days after successful verification
* Error and warning reporting

---

## Prerequisites for both servers

### Windows

* PowerShell
* OpenSSH Client
* SCP utility

### Linux

* SSH Server running
* User account with write access to the destination directory

---

## Configuration

Update the following variables before execution:

```powershell
$SourcePath = "C:\projects"
$LinuxUser  = "manish"
$LinuxIP    = "192.168.137.134"
$DestPath   = "/home/manish/Transfer"
```

| Variable   | Description                    |
| ---------- | ------------------------------ |
| SourcePath | Source directory on Windows    |
| LinuxUser  | Linux username                 |
| LinuxIP    | Linux server IP address        |
| DestPath   | Destination directory on Linux |

---

## Workflow

1. Connect to the Linux server via SSH.
2. Create the destination directory if it does not exist.
3. Generate a timestamped log file.
4. Scan all files recursively from the source directory.
5. Recreate the same folder structure on Linux.
6. Transfer files using SCP.
7. Verify transferred files by comparing file sizes.
8. Delete source files older than 7 days only if verification succeeds.
9. Record all activities in the log file.

---

## Logging

A log file is automatically generated for every execution:

```text
output_YYYY-MM-DD_HH-MM-SS.txt
```

The log includes information regarding:

* Transfer status
* Verification results
* Deleted files
* Warnings and errors
* Final execution summary

---

## Running the Script

Execute the script from PowerShell:

```powershell
.\WindowsToLinuxTransfer.ps1
```

---

## Safety Checks

Files are deleted from Windows only when:

* The file exists on the Linux server.
* The transferred file size matches the original file size.
* The file is older than 7 days.

This ensures data integrity and prevents accidental data loss.

---

## Use Case

Ideal for:

* Automated file archival
* Windows-to-Linux data migration
* Backup workflows
* Shared file processing environments
* Scheduled transfer and cleanup operations