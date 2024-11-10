# <span style="color:violet">Uwagi</span>
1. nie obsługuje DBISAM (Estima) - nie widać uprawnień w pliku user_a.dat
2. nie zbiera danych z SignUM, Orchestra, ...
3. 


# FORMAT
## role: *internal_id, name, description*
## użytkownicy: *internal_id, login, first_name, last_name*
*jesli imię i nazwisko są razem, to dać je do first_name, a last_name=''*'
## użytkownicy-role: *user_id, role_id*
*w relacji do odpowiednich internal_id*

<details>
<summary>groszek PDA, PDK</summary>


## role:
`
select trim(KOD_GRUPY) internal_id, trim(NAZWA) name, trim(coalesce(OPIS,'')) description from OP_GRUPY
union
select distinct 'UPR_'|| f.KOD_SYSTEMU || ':' || f.kod_funsys internal_id, '~UPR: ' || f.KOD_FUNSYS name, TRIM(rr.nazwa) || ': ' || trim(coalesce(f.OPIS,'')) description
from OP_SLFUN f
LEFT OUTER JOIN IS_REJESTR rr ON f.KOD_SYSTEMU = rr.ID_SYSTEMU
LEFT OUTER JOIN OP_OPFUN oof ON f.KOD_FUNSYS = oof.KOD_FUNSYS AND f.KOD_SYSTEMU = oof.KOD_SYSTEMU
`

--LEFT OUTER JOIN OP_OPER r ON r.KOD_OPER = oof.KOD_OPER AND r.STATUS = 'T'
## użytkownicy
select KOD_OPER internal_id, NAZWA login, trim(coalesce(NAZWA_ZEWN, NAZWA)) first_name, '' last_name from OP_OPER
where STATUS = 'T'
## użytkownicy-role
SELECT r.KOD_OPER user_id, r.KOD_GRUPY role_id
FROM OP_OPERGRUP r
join OP_OPER o
on o.KOD_OPER = r.KOD_OPER
where o.STATUS = 'T'
union
select opf.kod_oper user_id, 'UPR_'|| opf.KOD_SYSTEMU || ':' || opf.kod_funsys role_id
from op_opfun opf
inner join OP_OPER op ON op.KOD_OPER = opf.kod_oper and op.status = 'T'
</details>

# Groszek Umowy FV:
## role:
select distinct w.ID_WYDZIALU, w.KOD, w.NAZWA
FROM B_WYDZIAL_OPER r
join B_WYDZIALY w on w.ID_WYDZIALU = r.ID_WYDZIALU
where w.rok = (select max(rok) from B_WYDZIAL_OPER) and r.rok = (select max(rok) from B_WYDZIAL_OPER)
## użytkownicy:
select distinct o.KOD_OPER internal_id, o.NAZWA, trim(coalesce(NAZWA_ZEWN, NAZWA)) first_name, '' last_name from OP_OPER o
join B_wydzial_OPER r on o.KOD_OPER = r.KOD_OPER
where o.STATUS = 'T'
## użytkownicy-role:
select r.KOD_OPER user_id, r.ID_WYDZIALU role_id
from b_wydzial_oper r
where r.ROK = (select max(rok) from B_WYDZIAL_OPER) and r.rok = (select max(rok) from B_WYDZIAL_OPER)

# Groszek KSZOB
## role
select ID_SYSTEMU internal_id, NAZWA name, OPIS description from IS_REJESTR
## użytkownicy
select KOD_OPER internal_id, NAZWA login, trim(coalesce(NAZWA_ZEWN, NAZWA)) first_name, '' last_name from OP_OPER
where STATUS = 'T'
## użytkownicy-role
SELECT r.KOD_OPER user_id, r.ID_SYSTEMU role_id
FROM KZ_OPER2SYSTEM r
join OP_OPER o on o.KOD_oper = r.KOD_OPER
where o.STATUS = 'T'

# Papirus SQL
## role:
SELECT GROUPCODE internal_id, GROUPNAME name, '' description
FROM SH_USRGP

## użytkownicy:
select username internal_id, username login, firstname first_name, lastname last_name
from SH_USERS
where DEACTIVATION is null and userid > 8

*-- nie wiem jak wyeliminować starych użytkowników, więc jest userid > 8* 

## użytkownicy-role:
select username user_id, groupcode role_id
from sh_memsp

*-- ewentualnie usunąć nieaktywnych uzytkowników*


# SR
## role:
SELECT distinct um.modul_aplikacji||um.CZY_PRZEGLADANIE internal_id, 'moduł '|| m.SKROT || IIF(um.CZY_PRZEGLADANIE = 'T', ' przeglądanie', ' pełny') name, '' description
FROM AD_UZYTKOWNICY_MODULY um
join AD_MODULY_APLIKACJI m on um.MODUL_APLIKACJI=m.MODUL_INT
union
select distinct 'rola' || u.ROL_ID internal_id, r.NAZWA_ROLI, '' description
from ad_uzytkownicy u
join ad_role r on r.rola_id = u.ROL_ID

## użytkownicy:
select UZY_ID internal_id, LOGIN login, IMIE first_name, NAZWISKO last_name
from AD_UZYTKOWNICY
where (STATUS_KONTA = '01' or STATUS_KONTA = '03') and USUNIETY = 'N' and LOGIN <> 'SUPERADMIN'

## użytkownicy-role:
select uzy_id user_id, 'rola' || rol_id role_id
from ad_uzytkownicy
where (STATUS_KONTA = '01' or STATUS_KONTA = '03') and USUNIETY = 'N'
union
select um.uzy_id user_id, um.modul_aplikacji || um.CZY_PRZEGLADANIE role_id
from ad_uzytkownicy_moduly um
join ad_uzytkownicy u on u.UZY_ID = um.UZY_ID
where czy_wybrane = 'T' and
(u.STATUS_KONTA = '01' or u.STATUS_KONTA = '03') and u.USUNIETY = 'N'

# WINDOM
## role:
SELECT 1 internal_id, 'urzednik' name, 'obsługa wniosków i słowników' description
union
SELECT 2 internal_id, 'urzednik WOM' name, 'tylko podgląd' description
union
SELECT 3 internal_id, 'admin' name, 'ustawienia' description
union
SELECT 4 internal_id, 'obsluga wyplat' name, 'obsługa wypłat' description
union
SELECT 5 internal_id, 'admin_oper' name, 'administrator operatorów' description

## użytkownicy:
select ID_Operator internal_id, login login, imie first_name, Nazwisko last_name
from operator
where (DataZwolnienia is null) AND (czyurzednik<>0 OR czyurzednikwom<>0 OR czyadmin<>0 OR CzyObslugaWyplat<>0 OR CzyAdminOper<>0)

-- nie pokazuje użytkowników bez żadnych uprawnień

## użytkownicy-role:
select ID_Operator user_id, 1 role_id
from operator
where DataZwolnienia is null and CzyUrzednik = 1
union
select ID_Operator user_id, 2 role_id
from operator
where DataZwolnienia is null and CzyUrzednikWOM = 1
union
select ID_Operator user_id, 3 role_id
from operator
where DataZwolnienia is null and CzyAdmin = 1
union
select ID_Operator user_id, 4 role_id
from operator
where DataZwolnienia is null and CzyObslugaWyplat = 1
union
select ID_Operator user_id, 5 role_id
from operator
where DataZwolnienia is null and CzyAdminOper = 1


# OPTIest:
# role:
SELECT rol_ID internal_id, ROL_NAZWA name, '' description
from ROLE
where USUNIETY is null

## użytkownicy:
select  PRAC_ID, UZYTK_login login, PRAC_IMIE first_name, PRAC_NAZWISKO last_name
from v_lista_pracownicy
where PRAC_DATA_ZWOLNIENIA is null and PRAC_UZYTKOWNIK = 'T' and PRAC_USUNIETY is null and UZYTK_LOGIN is not null and PRAC_FULL <> 'agent agent'

## użytkownicy-role:
select PRCR_PRAC_ID user_id, PRCR_ROL_ID role_id
from PRACOWNICY_ROLE
where USUNIETY is null

# AD grupy dystrybucyjne:
## role:
Get-ADGroup -Filter * -SearchBase "OU=Distribution Groups,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl" -Property SamAccountName,Name,Description
| Select-Object -Property SamAccountName,Name,Description
| convertto-json

## użytkownicy:
$users = @()
foreach($group in Get-ADGroup -Filter * -SearchBase "OU=Distribution Groups,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
    $users += Get-ADGroupMember -Identity $group.samaccountname -Recursive | Where-Object {$_.objectClass -eq "user"}
}
$data = @()
foreach($us in $users){
    $data += Get-ADUser -Identity $us.samaccountname -Properties samaccountname,GivenName,Surname
    }
$data | select-object -Unique -Property SamAccountName,GivenName,Surname | convertto-json

## użytkownicy-role:
$roles = @()
foreach($group in Get-ADGroup -Filter * -SearchBase "OU=Distribution Groups,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
    $group_users = Get-ADGroupMember -Identity $group.SamAccountName -Recursive | Where-Object {$_.objectClass -eq "user"}
    foreach($user in $group_users) {
        $p = [PSCustomObject]@{
            User = $user.samaccountname
            Role = $group.samaccountname
            }
        $roles += $p
    }
}
$roles | select-object -Unique -Property * | convertto-json

# Q-matic
## role:
$qmatic_groups = 'QM-BusinessAdmin', `
'QM-Calendar', `
'QM-CalendarAdmin', `
'QM-CalendarRecepcja', `
'QM-HwMonitoring', `
'QM-Koordynator', `
'QM-Podglad', `
'QM-Recepcja', `
'QM-Statystyka', `
'QM-SystemAdmin', `
'QM-Terminal', `
'QM-UD-Wesola', `
'QM-UserAdmin'
Get-ADGroup -Filter * -SearchBase "OU=Qmatic Orchestra,OU=Security Groups,DC=bzmw,DC=gov,DC=pl" -Property SamAccountName,Name,Description | where-object {$_.name -in $qmatic_groups} `
| Select-Object -Property SamAccountName,Name,Description `
| ConvertTo-Json

## użytkownicy
$qmatic_groups = 'QM-BusinessAdmin', `
'QM-Calendar', `
'QM-CalendarAdmin', `
'QM-CalendarRecepcja', `
'QM-HwMonitoring', `
'QM-Koordynator', `
'QM-Podglad', `
'QM-Recepcja', `
'QM-Statystyka', `
'QM-SystemAdmin', `
'QM-Terminal', `
'QM-UD-Wesola', `
'QM-UserAdmin'
$users = @()
foreach($group in $qmatic_groups){ $users += Get-ADGroupMember -Identity $group | Where-Object {$_.objectClass -eq "user"} }
$data = @()
foreach($us in $users){ $data += Get-ADUser -Identity $us.samaccountname -Properties samaccountname,GivenName,Surname } $data | select-object -Unique -Property SamAccountName,GivenName,Surname | convertto-json

ale to daje bardzo dużo nadmiarowych użytkowników spoza UD Wesoła, więc sensowniejsze jest zapytanie:

$users = Get-ADGroupMember -Identity 'QM-UD-Wesola' | Where-Object {$_.objectClass -eq "user"}
$data = @()
foreach($us in $users){ $data += Get-ADUser -Identity $us.samaccountname -Properties samaccountname,GivenName,Surname } $data | select-object -Unique -Property SamAccountName,GivenName,Surname | convertto-json


## użytkownicy-role:
$qmatic_groups = 'QM-BusinessAdmin', `
'QM-Calendar', `
'QM-CalendarAdmin', `
'QM-CalendarRecepcja', `
'QM-HwMonitoring', `
'QM-Koordynator', `
'QM-Podglad', `
'QM-Recepcja', `
'QM-Statystyka', `
'QM-SystemAdmin', `
'QM-Terminal', `
'QM-UD-Wesola', `
'QM-UserAdmin'
$roles = @()
foreach($group in $qmatic_groups){ $group_users = Get-ADGroupMember -Identity $group | Where-Object {$_.objectClass -eq "user"}
    foreach($user in $group_users) { 
        $p = [PSCustomObject]@{
            User = $user.samaccountname 
            Role = $group
        }
        $roles += $p
    } 
} $roles | select-object -Unique -Property * | convertto-json


#PIUW
## użytkownicy:
convertto-json @(Get-ADGroup -Filter * -SearchBase "CN=piuw_wesola_rednacz,OU=PIUW,OU=.SecurityGroups,OU=.Konta Specjalne,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl" -Property SamAccountName,Name,Description | Select-Object -Property SamAccountName,Name,Description)

## role:
$users = @()
foreach($group in Get-ADGroup -Filter * -SearchBase "CN=piuw_wesola_rednacz,OU=PIUW,OU=.SecurityGroups,OU=.Konta Specjalne,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
    $users += Get-ADGroupMember -Identity $group.samaccountname -Recursive | Where-Object {$_.objectClass -eq "user"}
}
$data = @()
foreach($us in $users){
    $user = Get-ADUser -Identity $us.samaccountname -Properties samaccountname,GivenName,Surname
    if ($user.DistinguishedName -Match "OU=Users,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
        $data +=$user
    }
}
$data | select-object -Unique -Property SamAccountName,GivenName,Surname | convertto-json

## użytkownicy-role:
$users = @()
foreach($group in Get-ADGroup -Filter * -SearchBase "CN=piuw_wesola_rednacz,OU=PIUW,OU=.SecurityGroups,OU=.Konta Specjalne,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
    $users += Get-ADGroupMember -Identity $group.samaccountname -Recursive | Where-Object {$_.objectClass -eq "user"}
}
$roles = @()
foreach($user in $users) {
    if ($user.DistinguishedName -Match "OU=Users,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl"){
        $p = [PSCustomObject]@{
            User = $user.samaccountname
            Role = "piuw_wesola_rednacz"
            }
        $roles += $p
    }
}
$roles | select-object -Unique -Property * | convertto-json


----------------------------------------------------------------

Get-ADObject  -Filter * -SearchBase "CN=wesola.edukacjaprzedszkolna,OU=Poczta,OU=Distribution Groups,OU=Dzielnica,OU=Wesola,OU=Dzielnice,OU=Urzad Miasta Warszawy,DC=bzmw,DC=gov,DC=pl" -Properties *

__dopasowywanie użytkowników w systemach do kont w AD opiera się na imionach i nazwiskach (GivenName i Surname)__

__ważne jest ujednolicenie pól Office i Department w AD__