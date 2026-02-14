$ErrorActionPreference = 'Stop'
Set-Location 'C:\Users\junic\.openclaw\workspace'
New-Item -ItemType Directory -Path 'github_backup\memory_backup' -Force | Out-Null
if (Test-Path 'memory') {
  Copy-Item -Path 'memory\*' -Destination 'github_backup\memory_backup' -Recurse -Force
}
Copy-Item -Path 'faiss_metadata.json','faiss_memory.index','MEMORY.md' -Destination 'github_backup\memory_backup' -Force
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
git add .
git commit -m "Backup memories - $ts"
