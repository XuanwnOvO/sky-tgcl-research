$ProgressPreference='SilentlyContinue'
$urls = @(
 'https://sourceforge.net/projects/unluac/files/unluac_2024_06_21.jar/download',
 'https://master.dl.sourceforge.net/project/unluac/unluac_2024_06_21.jar?viasf=1',
 'https://sourceforge.net/projects/unluac/files/unluac_2023_04_05.jar/download',
 'https://master.dl.sourceforge.net/project/unluac/unluac_2022_09_20.jar?viasf=1'
)
$dst='D:\unluac.jar'
foreach ($u in $urls) {
  try {
    Invoke-WebRequest -Uri $u -OutFile $dst -UseBasicParsing -TimeoutSec 60 -MaximumRedirection 10
    $b=[IO.File]::ReadAllBytes($dst)
    if ($b.Length -gt 10000 -and $b[0] -eq 0x50 -and $b[1] -eq 0x4B) { "OK: $u ($($b.Length) bytes)"; break }
    else { "BAD content ($($b.Length) bytes, head $($b[0])): $u" }
  } catch { "FAIL: $u -- $($_.Exception.Message)" }
}
