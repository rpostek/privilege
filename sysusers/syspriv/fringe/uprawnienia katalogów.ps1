# wyświetla uprawnienia podkatalogów (z pominięciem grup ZINu)

$path = '\\fs04\files_ud_wesola$\ug\FINANSE'

Get-ChildItem -Path $path -Directory | ForEach-Object {
    Write-Output $_.FullName; (Get-Acl -Path $_.FullName).Access |
    `Select-Object -Property IdentityReference |
    `Where-Object -Property IdentityReference -Like 'BZMW\WES.*' |
    `Where-object -Property IdentityReference -NE 'BZMW\WES.TEX' |
    `Where-object -Property IdentityReference -NE 'BZMW\WES.WIN';
    `Write-Output ''}
