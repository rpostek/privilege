$path = '\\fs04\files_ud_wesola$\ug\FINANSE'
$files = @()
Get-ChildItem -Path $path -Directory | ForEach-Object {
    $name = $_.BaseName
    $r = (Get-Acl -Path $_.FullName).Access |
    `Select-Object -Property IdentityReference |
    `Where-Object -Property IdentityReference -Like 'BZMW\*wydatki*'
    if ($r -ne $null) {
        $files += $name
    }
}
Write-Output $files;
$fcs = $files -join ', '
Write-Output $fcs;
