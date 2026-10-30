$ProgressPreference='SilentlyContinue'
# Try multiple mirrors for unluac jar
$targets = @(
  'https://codeload.github.com/viruscamp/unluac/zip/refs/heads/master',
  'https://ghfast.top/https://github.com/viruscamp/unluac/archive/refs/heads/master.zip',
  'https://github.moeyy.xyz/https://github.com/viruscamp/unluac/archive/refs/heads/master.zip',
  'https://gh.llkk.cc/https://github.com/viruscamp/unluac/archive/refs/heads/master.zip'
)
$dst='D:\unluac_src.zip'
foreach ($u in $targets) {
  try {
    Invoke-WebRequest -Uri $u -OutFile $dst -UseBasicParsing -TimeoutSec 90 -UserAgent 'Mozilla/5.0'
    $b=[IO.File]::ReadAllBytes($dst)
    if ($b[0] -eq 0x50 -and $b[1] -eq 0x4B) { "OK $u $($b.Length)"; break } else { "BAD $u head=$($b[0])" }
  } catch { "FAIL $u -- $($_.Exception.Message)" }
}
